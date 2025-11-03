# routes/admin.py
import os
import re
import json
import sqlite3
from collections import Counter
from datetime import datetime, timedelta
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, current_app

# 导入现有的函数
from database.models import get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# 管理员仪表板路由
@admin_bp.route('/dashboard')
def dashboard():
    """管理员仪表板"""
    if 'role' in session and session['role'] == 'platform_admin':
        # 使用现有的get_articles函数
        from database.models import get_articles
        articles = get_articles()

        return render_template(
            'pages/admin_dashboard/admin_dashboard.html',
            username=session['username'],
            articles=articles
        )
    return redirect(url_for('auth.login'))


# 用户管理路由
@admin_bp.route('/manage_users')
def manage_users():
    """用户管理页面"""
    if 'role' in session and session['role'] == 'platform_admin':
        users = get_users()
        return render_template('pages/admin_dashboard/manage_users.html', users=users)
    return redirect(url_for('auth.login'))


@admin_bp.route('/system_settings')
def system_settings():
    """系统设置页面"""
    if 'role' in session and session['role'] == 'platform_admin':
        return render_template('pages/admin_dashboard/system_settings.html')
    return redirect(url_for('auth.login'))


@admin_bp.route('/global_analytics')
def global_analytics():
    """全局统计页面"""
    if 'role' in session and session['role'] == 'platform_admin':
        return render_template('pages/admin_dashboard/global_analytics.html')
    return redirect(url_for('auth.login'))


@admin_bp.route('/security_center')
def security_center():
    """安全中心页面"""
    if 'role' in session and session['role'] == 'platform_admin':
        return render_template('pages/admin_dashboard/security_center.html')
    return redirect(url_for('auth.login'))


# API 路由
@admin_bp.route('/api/users', methods=['GET'])
def api_get_users():
    """获取用户列表API"""
    if 'role' in session and session['role'] == 'platform_admin':
        users = get_users()
        return jsonify([dict(user) for user in users])
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/users', methods=['POST'])
def api_create_user():
    """创建用户API"""
    if 'role' in session and session['role'] == 'platform_admin':
        data = request.json
        success = create_user(
            username=data['username'],
            password=data['password'],
            role=data['role'],
            full_name=data.get('full_name', ''),
            org_name=data.get('org_name', '')
        )
        if success:
            return jsonify({'message': '用户创建成功'})
        return jsonify({'error': '用户创建失败'}), 400
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    """更新用户API"""
    if 'role' in session and session['role'] == 'platform_admin':
        data = request.json
        success = update_user(
            user_id=user_id,
            username=data['username'],
            role=data['role'],
            full_name=data.get('full_name', ''),
            org_name=data.get('org_name', '')
        )
        if success:
            return jsonify({'message': '用户更新成功'})
        return jsonify({'error': '用户更新失败'}), 400
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    """删除用户API"""
    if 'role' in session and session['role'] == 'platform_admin':
        success = delete_user(user_id)
        if success:
            return jsonify({'message': '用户删除成功'})
        return jsonify({'error': '用户删除失败'}), 400
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/articles/<int:article_id>')
def api_get_article(article_id):
    """获取文章详情API"""
    if 'role' in session and session['role'] == 'platform_admin':
        article = get_article_by_id(article_id)
        if article:
            return jsonify(dict(article))
        return jsonify({'error': '文章不存在'}), 404
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/articles/<int:article_id>', methods=['PUT'])
def api_update_article(article_id):
    """更新文章API"""
    if 'role' in session and session['role'] == 'platform_admin':
        data = request.json
        success = update_article(
            article_id=article_id,
            title=data['title'],
            content=data['content']
        )
        if success:
            return jsonify({'message': '文章更新成功'})
        return jsonify({'error': '文章更新失败'}), 400
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/articles/<int:article_id>', methods=['DELETE'])
def api_delete_article(article_id):
    """删除文章API"""
    if 'role' in session and session['role'] == 'platform_admin':
        success = delete_article(article_id)
        if success:
            return jsonify({'message': '文章删除成功'})
        return jsonify({'error': '文章删除失败'}), 400
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/system_settings', methods=['GET', 'PUT'])
def api_system_settings():
    """系统设置API"""
    if 'role' in session and session['role'] == 'platform_admin':
        if request.method == 'GET':
            settings = get_system_settings()
            return jsonify(settings)
        elif request.method == 'PUT':
            data = request.json
            success = update_system_settings(data)
            if success:
                return jsonify({'message': '系统设置更新成功'})
            return jsonify({'error': '系统设置更新失败'}), 400
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/analytics/data')
def api_analytics_data():
    """获取统计数据API"""
    if 'role' in session and session['role'] == 'platform_admin':
        data = get_analytics_data()
        return jsonify(data)
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/analytics/wordcloud')
def api_analytics_wordcloud():
    """获取词云数据API - 修改函数名避免冲突"""
    if 'role' in session and session['role'] == 'platform_admin':
        wordcloud_data = get_wordcloud_data()
        return jsonify(wordcloud_data)
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/analytics/users_table')
def api_analytics_users_table():
    """获取用户表格数据API"""
    if 'role' in session and session['role'] == 'platform_admin':
        users_data = get_users_table_data()
        return jsonify(users_data)
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/analytics/articles_table')
def api_analytics_articles_table():
    """获取文章表格数据API"""
    if 'role' in session and session['role'] == 'platform_admin':
        articles_data = get_articles_table_data()
        return jsonify(articles_data)
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/analytics/events_table')
def api_analytics_events_table():
    """获取事件表格数据API"""
    if 'role' in session and session['role'] == 'platform_admin':
        events_data = get_events_table_data()
        return jsonify(events_data)
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/analytics/courses_table')
def api_analytics_courses_table():
    """获取课程表格数据API"""
    if 'role' in session and session['role'] == 'platform_admin':
        courses_data = get_courses_table_data()
        return jsonify(courses_data)
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/security/logs')
def api_security_logs():
    """获取安全日志API"""
    if 'role' in session and session['role'] == 'platform_admin':
        logs = get_security_logs()
        return jsonify(logs)
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/database/tables')
def api_database_tables():
    """获取数据库表信息API"""
    if 'role' in session and session['role'] == 'platform_admin':
        tables = get_database_tables()
        return jsonify(tables)
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/database/table/<table_name>')
def api_database_table_data(table_name):
    """获取表数据API"""
    if 'role' in session and session['role'] == 'platform_admin':
        data = get_table_data(table_name)
        return jsonify(data)
    return jsonify({'error': 'Unauthorized'}), 401


@admin_bp.route('/api/database/execute', methods=['POST'])
def api_database_execute():
    """执行SQL语句API"""
    if 'role' in session and session['role'] == 'platform_admin':
        data = request.json
        result = execute_sql(data.get('sql', ''))
        return jsonify(result)
    return jsonify({'error': 'Unauthorized'}), 401


# 数据库操作函数
def get_users():
    """获取所有用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, role, full_name, org_name, created_at
            FROM users 
            ORDER BY created_at DESC
        ''')
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


def create_user(username, password, role, full_name="", org_name=""):
    """创建新用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password, role, full_name, org_name) VALUES (?, ?, ?, ?, ?)',
            (username, password, role, full_name, org_name)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False


def update_user(user_id, username, role, full_name="", org_name=""):
    """更新用户信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET username=?, role=?, full_name=?, org_name=? WHERE id=?',
            (username, role, full_name, org_name, user_id)
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error updating user: {e}")
        return False


def delete_user(user_id):
    """删除用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False


def get_article_by_id(article_id):
    """根据ID获取文章"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles WHERE id=?', (article_id,))
        article = cursor.fetchone()
        conn.close()
        return article
    except Exception as e:
        print(f"Error fetching article: {e}")
        return None


def update_article(article_id, title, content):
    """更新文章"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE articles SET title=?, content=? WHERE id=?',
            (title, content, article_id)
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error updating article: {e}")
        return False


def delete_article(article_id):
    """删除文章"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM articles WHERE id=?', (article_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error deleting article: {e}")
        return False


def get_system_settings():
    """获取系统设置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建系统设置表（如果不存在）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 插入默认设置（如果不存在）
        default_settings = [
            ('system_theme', 'default', '系统主题'),
            ('background_color', '#ffffff', '背景颜色'),
            ('layout_style', 'standard', '布局样式'),
            ('max_articles_per_page', '10', '每页文章数'),
            ('allow_registration', 'true', '允许用户注册'),
            ('maintenance_mode', 'false', '维护模式')
        ]

        for key, value, description in default_settings:
            cursor.execute('''
            INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
            VALUES (?, ?, ?)
            ''', (key, value, description))

        conn.commit()

        # 获取所有设置
        cursor.execute('SELECT setting_key, setting_value, description FROM system_settings')
        settings_data = cursor.fetchall()
        conn.close()

        settings = {row['setting_key']: row['setting_value'] for row in settings_data}
        return settings
    except Exception as e:
        print(f"Error getting system settings: {e}")
        return {}


def update_system_settings(settings):
    """更新系统设置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for key, value in settings.items():
            cursor.execute('''
            INSERT OR REPLACE INTO system_settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating system settings: {e}")
        return False


def get_analytics_data():
    """获取统计数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 基础统计
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
        student_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'")
        teacher_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'community_org'")
        organizer_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM articles")
        article_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]

        # 用户活跃度统计（简化版）
        cursor.execute("SELECT COUNT(*) FROM users WHERE last_login IS NOT NULL")
        active_users = cursor.fetchone()[0]

        # 文章分类统计
        cursor.execute('''
        SELECT 
            CASE 
                WHEN LENGTH(content) < 100 THEN 'Short story'
                WHEN LENGTH(content) < 500 THEN 'Medium-length story' 
                ELSE 'Long story'
            END as category,
            COUNT(*) as count
        FROM articles 
        GROUP BY category
        ''')
        article_categories = cursor.fetchall()

        conn.close()

        return {
            'user_stats': {
                'students': student_count,
                'teachers': teacher_count,
                'organizers': organizer_count,
                'total': student_count + teacher_count + organizer_count,
                'active': active_users
            },
            'content_stats': {
                'articles': article_count,
                'events': event_count,
                'courses': course_count,
                'recent_articles': 0,
                'recent_events': 0
            },
            'active_users': [
                {'role': 'student', 'count': student_count},
                {'role': 'teacher', 'count': teacher_count},
                {'role': 'community_org', 'count': organizer_count}
            ],
            'article_categories': [dict(row) for row in article_categories]
        }
    except Exception as e:
        print(f"Error getting analytics data: {e}")
        return {}


def get_wordcloud_data():
    """获取词云数据 - 简化版本，不使用jieba"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 英文停用词列表
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was',
            'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
            'them',
            'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
            'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            'can', 'just'
        }

        all_text = ""

        # 从文章表中获取标题和内容
        cursor.execute("SELECT title, content FROM articles")
        articles = cursor.fetchall()
        for article in articles:
            if article['title']:
                all_text += f" {article['title']}"
            if article['content']:
                all_text += f" {article['content']}"

        # 从事件表中获取标题和描述
        cursor.execute("SELECT title, description FROM events")
        events = cursor.fetchall()
        for event in events:
            if event['title']:
                all_text += f" {event['title']}"
            if event['description']:
                all_text += f" {event['description']}"

        # 从课程表中获取标题和描述
        cursor.execute("SELECT title, description FROM courses")
        courses = cursor.fetchall()
        for course in courses:
            if course['title']:
                all_text += f" {course['title']}"
            if course['description']:
                all_text += f" {course['description']}"

        # 简单的英文文本处理
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())

        # 统计词频
        word_freq = Counter()
        for word in words:
            if word not in stop_words:
                word_freq[word] += 1

        # 获取前30个最常见的词
        top_words = word_freq.most_common(30)

        # 转换为词云需要的格式
        wordcloud_data = []
        for word, freq in top_words:
            # 根据频率设置权重（1-20的范围）
            weight = min(20, max(3, freq))
            wordcloud_data.append({
                'text': word,
                'weight': weight,
                'freq': freq
            })

        conn.close()

        # 如果数据为空，返回默认数据
        if not wordcloud_data:
            wordcloud_data = get_default_wordcloud_data()

        return wordcloud_data

    except Exception as e:
        print(f"Error getting wordcloud data: {e}")
        # 如果出错，返回默认数据
        return get_default_wordcloud_data()


def get_default_wordcloud_data():
    """获取默认词云数据"""
    return [
        {'text': 'Education', 'weight': 13, 'freq': 25},
        {'text': 'Learning', 'weight': 12, 'freq': 22},
        {'text': 'Courses', 'weight': 11, 'freq': 20},
        {'text': 'Students', 'weight': 10, 'freq': 18},
        {'text': 'Teachers', 'weight': 9, 'freq': 16},
        {'text': 'Community', 'weight': 8, 'freq': 14},
        {'text': 'Events', 'weight': 7, 'freq': 12},
        {'text': 'Technology', 'weight': 6, 'freq': 10},
        {'text': 'Development', 'weight': 5, 'freq': 8},
        {'text': 'Programming', 'weight': 4, 'freq': 6},
        {'text': 'Projects', 'weight': 3, 'freq': 4},
        {'text': 'Collaboration', 'weight': 2, 'freq': 2}
    ]


def get_security_logs():
    """获取安全日志"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建日志表（如果不存在）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            description TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # 插入一些示例日志（如果表为空）
        cursor.execute("SELECT COUNT(*) FROM security_logs")
        if cursor.fetchone()[0] == 0:
            sample_logs = [
                (1, '用户登录', '管理员登录系统', '192.168.1.100', 'Mozilla/5.0...'),
                (None, '系统启动', '应用程序启动', '127.0.0.1', 'System'),
                (2, '用户注册', '新用户注册', '192.168.1.101', 'Mozilla/5.0...'),
                (1, '文章创建', '创建新文章', '192.168.1.100', 'Mozilla/5.0...')
            ]
            cursor.executemany('''
            INSERT INTO security_logs (user_id, action, description, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
            ''', sample_logs)
            conn.commit()

        # 获取最近的日志
        cursor.execute('''
        SELECT sl.*, u.username 
        FROM security_logs sl 
        LEFT JOIN users u ON sl.user_id = u.id 
        ORDER BY sl.created_at DESC 
        LIMIT 100
        ''')
        logs = cursor.fetchall()
        conn.close()

        return [dict(log) for log in logs]
    except Exception as e:
        print(f"Error getting security logs: {e}")
        return []


def get_database_tables():
    """获取数据库表信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        table_info = []
        for table in tables:
            table_name = table['name']
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = cursor.fetchone()['count']

            table_info.append({
                'name': table_name,
                'columns': [dict(col) for col in columns],
                'row_count': row_count
            })

        conn.close()
        return table_info
    except Exception as e:
        print(f"Error getting database tables: {e}")
        return []


def get_table_data(table_name):
    """获取表数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 安全验证表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            return {'error': '表不存在'}

        cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
        data = cursor.fetchall()
        conn.close()

        return [dict(row) for row in data]
    except Exception as e:
        print(f"Error getting table data: {e}")
        return {'error': str(e)}


def execute_sql(sql):
    """执行SQL语句"""
    try:
        if not sql.strip().upper().startswith(('SELECT', 'PRAGMA')):
            return {'error': '只允许执行SELECT和PRAGMA查询'}

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(sql)

        if sql.strip().upper().startswith('SELECT'):
            data = cursor.fetchall()
            result = [dict(row) for row in data]
        else:
            result = {'message': '执行成功'}

        conn.close()
        return {'data': result}
    except Exception as e:
        print(f"Error executing SQL: {e}")
        return {'error': str(e)}


def get_users_table_data():
    """获取用户表格数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                id, 
                username, 
                role, 
                full_name, 
                org_name, 
                created_at,
                last_login
            FROM users 
            ORDER BY created_at DESC
            LIMIT 100
        ''')
        users = cursor.fetchall()
        conn.close()

        # 转换为字典列表
        users_data = []
        for user in users:
            users_data.append({
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'full_name': user['full_name'] or 'N/A',
                'org_name': user['org_name'] or 'N/A',
                'registration_date': user['created_at'],
                'last_login': user['last_login'] or 'Never'
            })

        return users_data
    except Exception as e:
        print(f"Error fetching users table data: {e}")
        return []


def get_articles_table_data():
    """获取文章表格数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                a.id,
                a.title,
                u.full_name as author_name,
                LENGTH(a.content) as content_length,
                a.created_at,
                a.updated_at,
                0 as views  -- 暂时设为0，实际应用中可以从统计表获取
            FROM articles a
            LEFT JOIN users u ON a.author_id = u.id
            ORDER BY a.created_at DESC
            LIMIT 100
        ''')
        articles = cursor.fetchall()
        conn.close()

        # 转换为字典列表
        articles_data = []
        for article in articles:
            articles_data.append({
                'id': article['id'],
                'title': article['title'],
                'author': article['author_name'] or 'Unknown',
                'content_length': f"{article['content_length']} chars",
                'created_at': article['created_at'],
                'updated_at': article['updated_at'],
                'views': article['views']
            })

        return articles_data
    except Exception as e:
        print(f"Error fetching articles table data: {e}")
        return []


def get_events_table_data():
    """获取事件表格数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                e.id,
                e.title as event_name,
                u.full_name as organizer_name,
                e.event_date,
                e.location,
                e.max_participants,
                COALESCE(ep.participant_count, 0) as registered_count
            FROM events e
            LEFT JOIN users u ON e.organizer_id = u.id
            LEFT JOIN (
                SELECT event_id, COUNT(*) as participant_count 
                FROM event_participants 
                GROUP BY event_id
            ) ep ON e.id = ep.event_id
            ORDER BY e.event_date DESC
            LIMIT 100
        ''')
        events = cursor.fetchall()
        conn.close()

        # 转换为字典列表
        events_data = []
        for event in events:
            events_data.append({
                'id': event['id'],
                'event_name': event['event_name'],
                'organizer': event['organizer_name'] or 'Unknown',
                'date': event['event_date'],
                'location': event['location'] or 'N/A',
                'max_participants': event['max_participants'],
                'registered': event['registered_count']
            })

        return events_data
    except Exception as e:
        print(f"Error fetching events table data: {e}")
        return []


def get_courses_table_data():
    """获取课程表格数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                c.id,
                c.title as course_name,
                u.full_name as teacher_name,
                COALESCE(ce.student_count, 0) as student_count,
                c.created_at,
                'Active' as status,  -- 简化状态
                COALESCE(ce.avg_score, 0) as rating
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            LEFT JOIN (
                SELECT 
                    course_id, 
                    COUNT(*) as student_count,
                    AVG(score) as avg_score
                FROM course_enrollments 
                GROUP BY course_id
            ) ce ON c.id = ce.course_id
            ORDER BY c.created_at DESC
            LIMIT 100
        ''')
        courses = cursor.fetchall()
        conn.close()

        # 转换为字典列表
        courses_data = []
        for course in courses:
            courses_data.append({
                'id': course['id'],
                'course_name': course['course_name'],
                'teacher': course['teacher_name'] or 'Unknown',
                'student_count': course['student_count'],
                'created_at': course['created_at'],
                'status': course['status'],
                'rating': f"{course['rating']:.1f}" if course['rating'] else 'N/A'
            })

        return courses_data
    except Exception as e:
        print(f"Error fetching courses table data: {e}")
        return []