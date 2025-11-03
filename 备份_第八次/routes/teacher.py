# routes/teacher.py
import bcrypt
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database.models import get_teacher_dashboard_data, get_articles, get_db_connection
from utils.helpers import add_student, delete_student

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

# 预设头像URL列表
AVATAR_URLS = [
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_2689977510_2663943077_fm_253_fmt_auto_app_120_f_JPEG_o2yr5a.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285689/u_3767343659_1707298728_fm_253_fmt_auto_app_138_f_JPEG_bhzefm.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_2048403386_38307565_fm_253_fmt_auto_app_138_f_JPEG_iyjmi4.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_3816230571_720057739_fm_253_fmt_auto_app_120_f_JPEG_c1urfb.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_94149824_3403889984_fm_253_fmt_auto_app_138_f_JPEG_kqtnr7.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_3348666652_2040777776_fm_253_fmt_auto_app_138_f_JPEG_a4ev92.webp'
]


@teacher_bp.route('/dashboard')
def dashboard():
    """教师仪表板"""
    if 'username' not in session or session.get('role') != 'teacher':
        flash('请先登录教师账户。', 'error')
        return redirect(url_for('auth.login'))

    from database.models import get_teacher_dashboard_data, get_articles
    teacher_id = session.get('user_id')

    teacher_data = get_teacher_dashboard_data(teacher_id)
    articles = get_articles()

    return render_template('pages/teacher/teacher.html',
                           teacher_data=teacher_data,
                           articles=articles)


# routes/teacher.py - 部分更新
@teacher_bp.route('/courses', methods=['GET', 'POST'])
def courses():
    """课程管理页面"""
    if 'username' not in session or session.get('role') != 'teacher':
        flash('请先登录教师账户。', 'error')
        return redirect(url_for('auth.login'))

    teacher_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 处理表单提交
    if request.method == 'POST':
        # 添加课程
        if 'add_course' in request.form:
            title = request.form.get('title')
            description = request.form.get('description')

            # 插入新课程
            cursor.execute("""
            INSERT INTO courses (teacher_id, title, description)
            VALUES (?, ?, ?)
            """, (teacher_id, title, description))

            conn.commit()
            flash(f'课程 "{title}" 添加成功！', 'success')

        # 删除课程
        elif 'delete_course' in request.form:
            course_id = request.form.get('course_id')

            # 先删除相关的课程内容
            cursor.execute("DELETE FROM course_contents WHERE course_id = ?", (course_id,))

            # 删除课程-学生关联
            cursor.execute("DELETE FROM course_enrollments WHERE course_id = ?", (course_id,))

            # 删除课程
            cursor.execute("DELETE FROM courses WHERE id = ? AND teacher_id = ?", (course_id, teacher_id))

            conn.commit()
            flash('课程删除成功！', 'success')

    # 查询当前教师的课程及其统计信息
    cursor.execute("""
    SELECT 
        c.id, 
        c.title, 
        c.description, 
        c.created_at,
        COUNT(ce.student_id) as total_students,
        COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_students,
        AVG(ce.score) as average_score
    FROM courses c
    LEFT JOIN course_enrollments ce ON c.id = ce.course_id
    WHERE c.teacher_id = ?
    GROUP BY c.id
    ORDER BY c.created_at DESC
    """, (teacher_id,))

    courses = cursor.fetchall()
    conn.close()

    return render_template('pages/teacher/courses.html', courses=courses)


@teacher_bp.route('/course/<int:course_id>/students')
def course_students(course_id):
    """查看课程中的学生及其成绩"""
    if 'username' not in session or session.get('role') != 'teacher':
        flash('请先登录教师账户。', 'error')
        return redirect(url_for('auth.login'))

    teacher_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 验证课程属于当前教师
    cursor.execute("SELECT title FROM courses WHERE id = ? AND teacher_id = ?", (course_id, teacher_id))
    course = cursor.fetchone()

    if not course:
        flash('课程不存在或无权访问。', 'error')
        conn.close()
        return redirect(url_for('teacher.courses'))

    # 查询课程中的学生及其成绩
    cursor.execute("""
    SELECT 
        u.id,
        u.full_name,
        u.username as email,
        u.student_id,
        ce.score,
        ce.status,
        ce.enrollment_date
    FROM users u
    JOIN course_enrollments ce ON u.id = ce.student_id
    WHERE ce.course_id = ?
    ORDER BY u.full_name
    """, (course_id,))

    students = cursor.fetchall()
    conn.close()

    return render_template('pages/teacher/course_students.html',
                           course=course,
                           students=students,
                           course_id=course_id)


@teacher_bp.route('/students')
def students():
    if 'role' in session and session['role'] == 'teacher':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT s.* 
        FROM students s
        JOIN course_students cs ON s.id = cs.student_id
        JOIN courses c ON cs.course_id = c.id
        WHERE c.teacher_id = ?
        GROUP BY s.id
        """, (session['user_id'],))
        students = cursor.fetchall()
        conn.close()

        return render_template(
            'pages/teacher/students.html',
            username=session['username'],
            students=students
        )
    return redirect(url_for('auth.login'))


@teacher_bp.route('/analytics')
def analytics():
    """数据统计页面 - 更新为使用 course_enrollments 表"""
    if 'username' not in session or session.get('role') != 'teacher':
        flash('请先登录教师账户。', 'error')
        return redirect(url_for('auth.login'))

    teacher_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 获取课程统计数据 - 使用 course_enrollments 表
        cursor.execute("""
        SELECT 
            c.id,
            c.title,
            COUNT(ce.student_id) as total_students,
            COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_students,
            AVG(ce.score) as average_score,
            COUNT(CASE WHEN ce.score >= 90 THEN 1 END) as excellent_students,
            COUNT(CASE WHEN ce.score >= 60 AND ce.score < 90 THEN 1 END) as good_students,
            COUNT(CASE WHEN ce.score < 60 THEN 1 END) as failing_students
        FROM courses c
        LEFT JOIN course_enrollments ce ON c.id = ce.course_id
        WHERE c.teacher_id = ?
        GROUP BY c.id
        ORDER BY c.created_at DESC
        """, (teacher_id,))

        course_stats = cursor.fetchall()

        # 获取总体统计
        cursor.execute("""
        SELECT 
            COUNT(DISTINCT c.id) as total_courses,
            COUNT(DISTINCT ce.student_id) as total_students,
            AVG(ce.score) as overall_average_score,
            COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as total_completions
        FROM courses c
        LEFT JOIN course_enrollments ce ON c.id = ce.course_id
        WHERE c.teacher_id = ?
        """, (teacher_id,))

        overall_stats = cursor.fetchone()

    except Exception as e:
        print(f"获取统计数据错误: {e}")
        course_stats = []
        overall_stats = {
            'total_courses': 0,
            'total_students': 0,
            'overall_average_score': 0,
            'total_completions': 0
        }

    conn.close()

    return render_template('pages/teacher/analytics.html',
                           course_stats=course_stats,
                           overall_stats=overall_stats)

# routes/teacher.py - 更新学生管理路由
@teacher_bp.route('/students_management', methods=['GET', 'POST'])
def students_management():
    """学生管理页面 - 更新为使用course_enrollments表"""
    if 'username' not in session or session.get('role') != 'teacher':
        flash('请先登录教师账户。', 'error')
        return redirect(url_for('auth.login'))

    teacher_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 处理表单提交
    if request.method == 'POST':
        # 添加学生
        if 'add_student' in request.form:
            full_name = request.form.get('full_name')
            email = request.form.get('email')

            # 检查邮箱是否已存在
            cursor.execute("SELECT id FROM users WHERE username = ?", (email,))
            if cursor.fetchone():
                flash('该邮箱已存在，请使用其他邮箱。', 'error')
            else:
                # 创建密码哈希
                password_hash = bcrypt.hashpw("123123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                # 插入新学生
                cursor.execute("""
                INSERT INTO users (username, password, role, full_name)
                VALUES (?, ?, 'student', ?)
                """, (email, password_hash, full_name))

                new_student_id = cursor.lastrowid

                # 将学生添加到教师的所有课程中 - 使用course_enrollments表
                cursor.execute("SELECT id FROM courses WHERE teacher_id = ?", (teacher_id,))
                courses = cursor.fetchall()
                for course in courses:
                    cursor.execute("""
                    INSERT OR IGNORE INTO course_enrollments (course_id, student_id)
                    VALUES (?, ?)
                    """, (course['id'], new_student_id))

                conn.commit()
                flash(f'学生 {full_name} 添加成功！默认密码为 123123', 'success')

        # 删除学生
        elif 'delete_student' in request.form:
            student_id = request.form.get('student_id')

            # 从教师的课程中移除学生 - 使用course_enrollments表
            cursor.execute("""
            DELETE FROM course_enrollments 
            WHERE student_id = ? 
            AND course_id IN (SELECT id FROM courses WHERE teacher_id = ?)
            """, (student_id, teacher_id))

            conn.commit()
            flash('学生删除成功！', 'success')

    # 查询当前教师的学生 - 更新为使用course_enrollments表
    cursor.execute("""
    SELECT DISTINCT u.id, u.username as email, u.full_name, u.created_at
    FROM users u
    JOIN course_enrollments ce ON u.id = ce.student_id
    JOIN courses c ON ce.course_id = c.id
    WHERE c.teacher_id = ? AND u.role = 'student'
    ORDER BY u.created_at DESC
    """, (teacher_id,))

    students = cursor.fetchall()
    conn.close()

    return render_template('pages/teacher/students_management.html', students=students)


@teacher_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """教师个人资料页面"""
    if 'username' not in session or session.get('role') != 'teacher':
        flash('请先登录教师账户。', 'error')
        return redirect(url_for('auth.login'))

    teacher_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取教师详细信息
    cursor.execute("""
    SELECT username, full_name, teacher_id, department, avatar, created_at
    FROM users 
    WHERE id = ?
    """, (teacher_id,))

    teacher_info = cursor.fetchone()

    # 处理表单提交
    if request.method == 'POST':
        # 修改密码
        if 'change_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # 验证当前密码
            cursor.execute("SELECT password FROM users WHERE id = ?", (teacher_id,))
            user = cursor.fetchone()

            if bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
                if new_password == confirm_password:
                    # 更新密码
                    new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password_hash, teacher_id))
                    conn.commit()
                    flash('密码修改成功！', 'success')
                else:
                    flash('新密码和确认密码不匹配。', 'error')
            else:
                flash('当前密码错误。', 'error')

        # 更新个人信息
        elif 'update_profile' in request.form:
            full_name = request.form.get('full_name')
            department = request.form.get('department')

            cursor.execute("""
            UPDATE users 
            SET full_name = ?, department = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (full_name, department, teacher_id))

            conn.commit()

            # 更新会话中的姓名
            session['full_name'] = full_name

            flash('个人信息更新成功！', 'success')

        # 更新头像
        elif 'update_avatar' in request.form:
            avatar = request.form.get('avatar')

            if avatar:
                cursor.execute("""
                UPDATE users 
                SET avatar = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """, (avatar, teacher_id))

                conn.commit()

                # 更新会话中的头像
                session['avatar'] = avatar

                flash('头像更新成功！', 'success')
            else:
                flash('请选择一个头像。', 'error')

    # 重新获取教师信息（可能已更新）
    cursor.execute("""
    SELECT username, full_name, teacher_id, department, avatar, created_at
    FROM users 
    WHERE id = ?
    """, (teacher_id,))

    teacher_info = cursor.fetchone()
    conn.close()

    return render_template('pages/teacher/profile.html',
                           teacher_info=teacher_info,
                           avatars=AVATAR_URLS)


