# # app.py
# from flask import Flask, render_template, request, redirect, url_for, session
# import sqlite3
# import os
# import time
# from flask import flash
#
# app = Flask(__name__)
# app.secret_key = 'your_secret_key'
# app.config['DATABASE'] = 'database/komodo_hub.db'
#
#
# # 初始化数据库
# def init_db():
#     # 检查数据库文件是否存在
#     if not os.path.exists(app.config['DATABASE']):
#         from database.init_database import init_database
#         init_database()
#         print("数据库已初始化")
#     else:
#         # 检查表结构是否需要更新
#         conn = get_db_connection()
#         cursor = conn.cursor()
#
#         # 检查用户表是否存在
#         cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
#         users_table_exists = cursor.fetchone() is not None
#
#         conn.close()
#
#         if not users_table_exists:
#             from database.init_database import init_database
#             init_database()
#             print("数据库表结构已更新")
#
#
# # 获取数据库连接
# def get_db_connection():
#     conn = sqlite3.connect(app.config['DATABASE'])
#     conn.row_factory = sqlite3.Row
#     return conn
#
#
# # 获取文章数据
# def get_articles():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute('SELECT * FROM articles ORDER BY created_at DESC')
#         articles = cursor.fetchall()
#         conn.close()
#         return articles
#     except Exception as e:
#         print(f"Error fetching articles: {e}")
#         return []
#
#
# # 获取教师仪表板数据
# def get_teacher_dashboard_data(teacher_id):
#     conn = get_db_connection()
#
#     try:
#         # 获取课程数量
#         cursor = conn.cursor()
#         cursor.execute("SELECT COUNT(*) as count FROM courses WHERE teacher_id = ?", (teacher_id,))
#         course_count_result = cursor.fetchone()
#         course_count = course_count_result['count'] if course_count_result else 0
#
#         # 获取学生数量
#         cursor.execute("""
#         SELECT COUNT(DISTINCT s.id) as count
#         FROM students s
#         JOIN course_students cs ON s.id = cs.student_id
#         JOIN courses c ON cs.course_id = c.id
#         WHERE c.teacher_id = ?
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
#                 # 如果没有统计数据，创建默认数据
#                 cursor.execute("""
#                 INSERT INTO course_statistics (course_id, total_students, completed_students, average_score)
#                 VALUES (?, 0, 0, 0)
#                 """, (course['id'],))
#                 conn.commit()
#
#                 # 重新获取统计数据
#                 cursor.execute("""
#                 SELECT c.id, c.title, cs.total_students, cs.completed_students, cs.average_score
#                 FROM courses c
#                 JOIN course_statistics cs ON c.id = cs.course_id
#                 WHERE c.id = ?
#                 """, (course['id'],))
#                 updated_course = cursor.fetchone()
#
#                 # 更新课程统计数据
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
#
# # 登录路由
# @app.route('/')
# def index():
#     return redirect(url_for('login'))
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#
#         # 连接到数据库
#         conn = get_db_connection()
#         cursor = conn.cursor()
#
#         # 查询用户信息
#         cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
#         user = cursor.fetchone()
#
#         conn.close()
#
#         if user:
#             session['username'] = username
#             session['role'] = user['role']
#             session['user_id'] = user['id']
#
#             if user['role'] == 'teacher':
#                 return redirect(url_for('teacher_dashboard'))
#             elif user['role'] == 'student':
#                 return redirect(url_for('student_dashboard'))
#             elif user['role'] == 'community_org':
#                 return redirect(url_for('community_dashboard'))
#             elif user['role'] == 'platform_admin':
#                 return redirect(url_for('admin_dashboard'))
#         else:
#             return "用户名或密码错误，请重试。"
#
#     return render_template('pages/login/login.html')
#
#
# # 教师仪表板路由
# @app.route('/teacher_dashboard')
# def teacher_dashboard():
#     if 'role' in session and session['role'] == 'teacher':
#         # 获取教师ID
#         conn = get_db_connection()
#         cursor = conn.cursor()
#
#         # 获取教师基本信息
#         cursor.execute("SELECT id, username FROM users WHERE id = ?", (session['user_id'],))
#         teacher_info = cursor.fetchone()
#
#         # 获取课程数量
#         cursor.execute("SELECT COUNT(*) as count FROM courses WHERE teacher_id = ?", (session['user_id'],))
#         course_count = cursor.fetchone()['count']
#
#         # 获取学生数量
#         cursor.execute("""
#         SELECT COUNT(DISTINCT s.id) as count
#         FROM students s
#         JOIN course_students cs ON s.id = cs.student_id
#         JOIN courses c ON cs.course_id = c.id
#         WHERE c.teacher_id = ?
#         """, (session['user_id'],))
#         student_count = cursor.fetchone()['count']
#
#         # 获取课程统计数据
#         cursor.execute("""
#         SELECT c.id, c.title, cs.total_students, cs.completed_students, cs.average_score
#         FROM courses c
#         LEFT JOIN course_statistics cs ON c.id = cs.course_id
#         WHERE c.teacher_id = ?
#         """, (session['user_id'],))
#         course_stats = cursor.fetchall()
#
#         # 获取文章数据
#         cursor.execute("SELECT * FROM articles ORDER BY created_at DESC")
#         articles = cursor.fetchall()
#
#         conn.close()
#
#         # 确保所有数据都有值
#         teacher_data = {
#             'course_count': course_count or 0,
#             'student_count': student_count or 0,
#             'course_stats': course_stats or []
#         }
#
#         return render_template(
#             'pages/teacher/teacher.html',  # 更新为新的模板路径
#             username=session['username'],
#             articles=articles,
#             teacher_data=teacher_data,
#             teacher_info=teacher_info
#         )
#     return redirect(url_for('login'))
#
# # 学生仪表板路由
# @app.route('/student_dashboard')
# def student_dashboard():
#     if 'role' in session and session['role'] == 'student':
#         # 获取文章数据
#         articles = get_articles()
#
#         return render_template(
#             'pages/student/student.html',
#             username=session['username'],
#             articles=articles
#         )
#     return redirect(url_for('login'))
#
#
# # 社区组织仪表板路由
# @app.route('/community_dashboard')
# def community_dashboard():
#     if 'role' in session and session['role'] == 'community_org':
#         # 获取文章数据
#         articles = get_articles()
#
#         return render_template(
#             'pages/community/community.html',
#             username=session['username'],
#             articles=articles
#         )
#     return redirect(url_for('login'))
#
#
# # 管理员仪表板路由
# @app.route('/admin_dashboard')
# def admin_dashboard():
#     if 'role' in session and session['role'] == 'platform_admin':
#         # 获取文章数据
#         articles = get_articles()
#
#         return render_template(
#             'pages/admin_dashboard/admin_dashboard.html',
#             username=session['username'],
#             articles=articles
#         )
#     return redirect(url_for('login'))
#
#
# # 添加教师功能路由
# @app.route('/teacher/courses')
# def teacher_courses():
#     if 'role' in session and session['role'] == 'teacher':
#         # 获取教师的课程
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM courses WHERE teacher_id = ?", (session['user_id'],))
#         courses = cursor.fetchall()
#         conn.close()
#
#         return render_template(
#             'pages/teacher/courses.html',
#             username=session['username'],
#             courses=courses
#         )
#     return redirect(url_for('login'))
#
#
# @app.route('/teacher/students')
# def teacher_students():
#     if 'role' in session and session['role'] == 'teacher':
#         # 获取教师的学生
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("""
#         SELECT s.*
#         FROM students s
#         JOIN course_students cs ON s.id = cs.student_id
#         JOIN courses c ON cs.course_id = c.id
#         WHERE c.teacher_id = ?
#         GROUP BY s.id
#         """, (session['user_id'],))
#         students = cursor.fetchall()
#         conn.close()
#
#         return render_template(
#             'pages/teacher/students.html',
#             username=session['username'],
#             students=students
#         )
#     return redirect(url_for('login'))
#
#
# @app.route('/teacher/analytics')
# def teacher_analytics():
#     if 'role' in session and session['role'] == 'teacher':
#         # 获取课程统计数据
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("""
#         SELECT c.title, cs.total_students, cs.completed_students, cs.average_score
#         FROM courses c
#         JOIN course_statistics cs ON c.id = cs.course_id
#         WHERE c.teacher_id = ?
#         """, (session['user_id'],))
#         analytics = cursor.fetchall()
#         conn.close()
#
#         return render_template(
#             'pages/teacher/analytics.html',
#             username=session['username'],
#             analytics=analytics
#         )
#     return redirect(url_for('login'))
#
#
# @app.route('/teacher/students_management', methods=['GET', 'POST'])
# def teacher_students_management():
#     if 'role' in session and session['role'] == 'teacher':
#         conn = get_db_connection()
#
#         if request.method == 'POST':
#             # 处理添加学生请求
#             if 'add_student' in request.form:
#                 full_name = request.form.get('full_name')
#                 email = request.form.get('email')
#
#                 try:
#                     # 首先创建用户账户
#                     cursor = conn.cursor()
#                     # 生成用户名和密码
#                     username = email.split('@')[0] if email else f"student{int(time.time())}"
#                     password = "123456"  # 默认密码，应该让用户首次登录后修改
#
#                     cursor.execute(
#                         "INSERT INTO users (username, password, role) VALUES (?, ?, 'student')",
#                         (username, password)
#                     )
#                     user_id = cursor.lastrowid
#
#                     # 创建学生记录
#                     cursor.execute(
#                         "INSERT INTO students (user_id, full_name, email) VALUES (?, ?, ?)",
#                         (user_id, full_name, email)
#                     )
#                     student_id = cursor.lastrowid
#
#                     # 将学生添加到教师的所有课程中
#                     cursor.execute("SELECT id FROM courses WHERE teacher_id = ?", (session['user_id'],))
#                     courses = cursor.fetchall()
#
#                     for course in courses:
#                         cursor.execute(
#                             "INSERT INTO course_students (course_id, student_id) VALUES (?, ?)",
#                             (course['id'], student_id)
#                         )
#
#                     conn.commit()
#                     flash('学生添加成功！', 'success')
#                 except Exception as e:
#                     conn.rollback()
#                     flash(f'添加学生失败: {str(e)}', 'error')
#
#             # 处理删除学生请求
#             elif 'delete_student' in request.form:
#                 student_id = request.form.get('student_id')
#
#                 try:
#                     cursor = conn.cursor()
#
#                     # 先从课程-学生关联表中删除
#                     cursor.execute("DELETE FROM course_students WHERE student_id = ?", (student_id,))
#
#                     # 然后从学生表中删除
#                     cursor.execute("SELECT user_id FROM students WHERE id = ?", (student_id,))
#                     student = cursor.fetchone()
#
#                     if student:
#                         user_id = student['user_id']
#                         cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
#
#                         # 最后从用户表中删除
#                         cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
#
#                     conn.commit()
#                     flash('学生删除成功！', 'success')
#                 except Exception as e:
#                     conn.rollback()
#                     flash(f'删除学生失败: {str(e)}', 'error')
#
#         # 获取教师的学生列表
#         cursor = conn.cursor()
#         cursor.execute("""
#         SELECT s.id, s.full_name, s.email, s.created_at
#         FROM students s
#         JOIN course_students cs ON s.id = cs.student_id
#         JOIN courses c ON cs.course_id = c.id
#         WHERE c.teacher_id = ?
#         GROUP BY s.id
#         ORDER BY s.created_at DESC
#         """, (session['user_id'],))
#         students = cursor.fetchall()
#
#         conn.close()
#
#         return render_template(
#             'pages/teacher/students_management.html',
#             username=session['username'],
#             students=students
#         )
#     return redirect(url_for('login'))
#
# # 退出登录路由
# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     session.pop('role', None)
#     session.pop('user_id', None)
#     return redirect(url_for('login'))
#
#
# if __name__ == '__main__':
#     init_db()  # 初始化数据库
#     app.run(debug=True)


from flask import Flask, redirect
from config import Config
from database.models import init_db
from routes.auth import auth_bp
from routes.teacher import teacher_bp
from routes.student import student_bp
from routes.community import community_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'your-secret-key-here'

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(admin_bp)

    # 初始化数据库
    with app.app_context():
        init_db()

    # 根路由重定向到登录
    @app.route('/')
    def index():
        return redirect('/login')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config['DEBUG'])