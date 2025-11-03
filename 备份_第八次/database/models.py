# database/models.py
import sqlite3
from flask import current_app
import os


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库"""
    from database.init_database import init_database
    init_database()


def get_articles():
    """获取文章数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles ORDER BY created_at DESC')
        articles = cursor.fetchall()
        conn.close()
        return articles
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []


# def get_teacher_dashboard_data(teacher_id):
#     """获取教师仪表板数据"""
#     conn = get_db_connection()
#
#     try:
#         # 获取课程数量
#         cursor = conn.cursor()
#         cursor.execute("SELECT COUNT(*) as count FROM courses WHERE teacher_id = ?", (teacher_id,))
#         course_count_result = cursor.fetchone()
#         course_count = course_count_result['count'] if course_count_result else 0
#
#         # 获取学生数量 - 更新为从users表查询
#         cursor.execute("""
#         SELECT COUNT(DISTINCT u.id) as count
#         FROM users u
#         JOIN course_students cs ON u.id = cs.student_id
#         JOIN courses c ON cs.course_id = c.id
#         WHERE c.teacher_id = ? AND u.role = 'student'
#         """, (teacher_id,))
#         student_count_result = cursor.fetchone()
#         student_count = student_count_result['count'] if student_count_result else 0
#
#         # 获取课程统计数据
#         cursor.execute("""
#         SELECT c.id, c.title, cs.total_students, cs.completed_students, cs.average_score
#         FROM courses c
#         LEFT JOIN course_statistics cs ON c.id = cs.course_id
#         WHERE c.teacher_id = ?
#         """, (teacher_id,))
#         course_stats = cursor.fetchall()
#
#         # 确保所有课程都有统计数据
#         for course in course_stats:
#             if course['total_students'] is None:
#                 cursor.execute("""
#                 INSERT INTO course_statistics (course_id, total_students, completed_students, average_score)
#                 VALUES (?, 0, 0, 0)
#                 """, (course['id'],))
#                 conn.commit()
#
#                 cursor.execute("""
#                 SELECT c.id, c.title, cs.total_students, cs.completed_students, cs.average_score
#                 FROM courses c
#                 JOIN course_statistics cs ON c.id = cs.course_id
#                 WHERE c.id = ?
#                 """, (course['id'],))
#                 updated_course = cursor.fetchone()
#
#                 course_stats = [updated_course if c['id'] == course['id'] else c for c in course_stats]
#
#         return {
#             'course_count': course_count,
#             'student_count': student_count,
#             'course_stats': course_stats
#         }
#     except Exception as e:
#         print(f"Error getting teacher dashboard data: {e}")
#         return {
#             'course_count': 0,
#             'student_count': 0,
#             'course_stats': []
#         }
#     finally:
#         conn.close()

# database/models.py
# database/models.py - 确保这个函数使用 course_enrollments
def get_teacher_dashboard_data(teacher_id):
    """获取教师仪表板数据 - 更新为使用course_enrollments表"""
    conn = get_db_connection()

    try:
        # 获取课程数量
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM courses WHERE teacher_id = ?", (teacher_id,))
        course_count_result = cursor.fetchone()
        course_count = course_count_result['count'] if course_count_result else 0

        # 获取学生数量 - 更新为从course_enrollments表查询
        cursor.execute("""
        SELECT COUNT(DISTINCT u.id) as count 
        FROM users u
        JOIN course_enrollments ce ON u.id = ce.student_id
        JOIN courses c ON ce.course_id = c.id
        WHERE c.teacher_id = ? AND u.role = 'student'
        """, (teacher_id,))
        student_count_result = cursor.fetchone()
        student_count = student_count_result['count'] if student_count_result else 0

        # 获取课程统计数据 - 更新为从course_enrollments表查询
        cursor.execute("""
        SELECT 
            c.id, 
            c.title, 
            COUNT(ce.student_id) as total_students,
            COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_students,
            AVG(ce.score) as average_score
        FROM courses c
        LEFT JOIN course_enrollments ce ON c.id = ce.course_id
        WHERE c.teacher_id = ?
        GROUP BY c.id
        ORDER BY c.created_at DESC
        """, (teacher_id,))
        course_stats = cursor.fetchall()

        return {
            'course_count': course_count,
            'student_count': student_count,
            'course_stats': course_stats
        }
    except Exception as e:
        print(f"Error getting teacher dashboard data: {e}")
        return {
            'course_count': 0,
            'student_count': 0,
            'course_stats': []
        }
    finally:
        conn.close()


def get_events(limit=None):
    """获取活动数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
        SELECT e.*, u.full_name as organizer_name, u.org_name
        FROM events e
        JOIN users u ON e.organizer_id = u.id
        ORDER BY e.event_date, e.event_time
        '''
        if limit:
            query += f' LIMIT {limit}'
        cursor.execute(query)
        events = cursor.fetchall()
        conn.close()
        return events
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def get_community_events(organizer_id):
    """获取特定社区组织的活动"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT e.*, COUNT(ep.id) as participant_count
        FROM events e
        LEFT JOIN event_participants ep ON e.id = ep.event_id
        WHERE e.organizer_id = ?
        GROUP BY e.id
        ORDER BY e.event_date, e.event_time
        ''', (organizer_id,))
        events = cursor.fetchall()
        conn.close()
        return events
    except Exception as e:
        print(f"Error fetching community events: {e}")
        return []

def create_event(title, description, organizer_id, event_date, event_time, location, max_participants):
    """创建新活动"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO events (title, description, organizer_id, event_date, event_time, location, max_participants)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, organizer_id, event_date, event_time, location, max_participants))
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id
    except Exception as e:
        print(f"Error creating event: {e}")
        return None

def delete_event(event_id, organizer_id):
    """删除活动（只能删除自己组织的活动）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 先删除参与记录
        cursor.execute('DELETE FROM event_participants WHERE event_id = ?', (event_id,))
        # 再删除活动
        cursor.execute('DELETE FROM events WHERE id = ? AND organizer_id = ?', (event_id, organizer_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error deleting event: {e}")
        return False













def get_users():
    """获取所有用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role, full_name, org_name, created_at FROM users ORDER BY created_at DESC')
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


# 在 database/models.py 的现有函数后面添加以下内容

def get_users():
    """获取所有用户"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, role, full_name, org_name, created_at, last_login 
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


def get_courses():
    """获取所有课程"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, u.full_name as teacher_name 
            FROM courses c 
            LEFT JOIN users u ON c.teacher_id = u.id 
            ORDER BY c.created_at DESC
        ''')
        courses = cursor.fetchall()
        conn.close()
        return courses
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []


def get_course_enrollments():
    """获取课程注册信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ce.*, u.full_name as student_name, c.title as course_title
            FROM course_enrollments ce
            JOIN users u ON ce.student_id = u.id
            JOIN courses c ON ce.course_id = c.id
            ORDER BY ce.enrolled_at DESC
        ''')
        enrollments = cursor.fetchall()
        conn.close()
        return enrollments
    except Exception as e:
        print(f"Error fetching course enrollments: {e}")
        return []


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
            ('maintenance_mode', 'false', '维护模式'),
            ('session_timeout', '60', '会话超时时间（分钟）'),
            ('backup_interval', '7', '自动备份间隔（天）')
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

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'community_organizer'")
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

        # 文章分类统计（简化版）
        cursor.execute('''
        SELECT 
            CASE 
                WHEN LENGTH(content) < 100 THEN '短篇'
                WHEN LENGTH(content) < 500 THEN '中篇' 
                ELSE '长篇'
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
                'recent_articles': 0,  # 简化处理
                'recent_events': 0  # 简化处理
            },
            'active_users': [
                {'role': 'student', 'count': student_count},
                {'role': 'teacher', 'count': teacher_count},
                {'role': 'community_organizer', 'count': organizer_count}
            ],
            'article_categories': [dict(row) for row in article_categories]
        }
    except Exception as e:
        print(f"Error getting analytics data: {e}")
        return {}


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