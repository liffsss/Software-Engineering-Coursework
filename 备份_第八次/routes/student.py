# routes/student.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.models import get_db_connection
import random

student_bp = Blueprint('student', __name__, url_prefix='/student')

# 预设头像URL列表
AVATAR_URLS = [
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_2689977510_2663943077_fm_253_fmt_auto_app_120_f_JPEG_o2yr5a.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285689/u_3767343659_1707298728_fm_253_fmt_auto_app_138_f_JPEG_bhzefm.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_2048403386_38307565_fm_253_fmt_auto_app_138_f_JPEG_iyjmi4.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_3816230571_720057739_fm_253_fmt_auto_app_120_f_JPEG_c1urfb.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_94149824_3403889984_fm_253_fmt_auto_app_138_f_JPEG_kqtnr7.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_3348666652_2040777776_fm_253_fmt_auto_app_138_f_JPEG_a4ev92.webp'
]


@student_bp.route('/dashboard')
def dashboard():
    """学生仪表板"""
    if 'username' not in session or session.get('role') != 'student':
        flash('请先登录学生账户。', 'error')
        return redirect(url_for('auth.login'))

    student_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取学生基本信息
    cursor.execute("SELECT full_name, student_id, grade FROM users WHERE id = ?", (student_id,))
    student_info = cursor.fetchone()

    # 获取学生已注册的课程
    cursor.execute("""
    SELECT 
        c.id,
        c.title,
        c.description,
        ce.score,
        ce.status,
        ce.enrollment_date,
        u.full_name as teacher_name
    FROM courses c
    JOIN course_enrollments ce ON c.id = ce.course_id
    JOIN users u ON c.teacher_id = u.id
    WHERE ce.student_id = ?
    ORDER BY ce.enrollment_date DESC
    """, (student_id,))

    enrolled_courses = cursor.fetchall()

    # 获取所有可选课程（未注册的）
    cursor.execute("""
    SELECT 
        c.id,
        c.title,
        c.description,
        u.full_name as teacher_name,
        COUNT(ce.student_id) as enrolled_students
    FROM courses c
    JOIN users u ON c.teacher_id = u.id
    LEFT JOIN course_enrollments ce ON c.id = ce.course_id AND ce.student_id = ?
    WHERE ce.student_id IS NULL
    GROUP BY c.id
    ORDER BY c.created_at DESC
    """, (student_id,))

    available_courses = cursor.fetchall()

    conn.close()

    return render_template('pages/student/student.html',
                           student_info=student_info,
                           enrolled_courses=enrolled_courses,
                           available_courses=available_courses)

@student_bp.route('/courses')
def courses():
    """学生课程页面"""
    if 'username' not in session or session.get('role') != 'student':
        flash('请先登录学生账户。', 'error')
        return redirect(url_for('auth.login'))

    student_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取学生基本信息
    cursor.execute("SELECT full_name, student_id, grade FROM users WHERE id = ?", (student_id,))
    student_info = cursor.fetchone()

    # 获取学生已注册的课程
    cursor.execute("""
    SELECT 
        c.id,
        c.title,
        c.description,
        ce.score,
        ce.status,
        ce.enrollment_date,
        u.full_name as teacher_name
    FROM courses c
    JOIN course_enrollments ce ON c.id = ce.course_id
    JOIN users u ON c.teacher_id = u.id
    WHERE ce.student_id = ?
    ORDER BY 
        CASE 
            WHEN ce.status = 'enrolled' THEN 1
            WHEN ce.status = 'completed' THEN 2
            ELSE 3
        END,
        ce.enrollment_date DESC
    """, (student_id,))

    courses = cursor.fetchall()

    conn.close()

    return render_template('pages/student/courses.html',
                           student_info=student_info,
                           courses=courses)


@student_bp.route('/enroll_course/<int:course_id>')
def enroll_course(course_id):
    """学生注册课程"""
    if 'username' not in session or session.get('role') != 'student':
        flash('请先登录学生账户。', 'error')
        return redirect(url_for('auth.login'))

    student_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 检查是否已经注册
        cursor.execute("""
        SELECT id FROM course_enrollments 
        WHERE course_id = ? AND student_id = ?
        """, (course_id, student_id))

        existing_enrollment = cursor.fetchone()

        if existing_enrollment:
            flash('您已经注册了这门课程。', 'info')
        else:
            # 注册新课程
            cursor.execute("""
            INSERT INTO course_enrollments (course_id, student_id, status)
            VALUES (?, ?, 'enrolled')
            """, (course_id, student_id))

            conn.commit()
            flash('课程注册成功！', 'success')

    except Exception as e:
        conn.rollback()
        print(f"注册课程错误: {e}")
        flash('注册课程失败，请重试。', 'error')
    finally:
        conn.close()

    return redirect(url_for('student.courses'))


@student_bp.route('/study_course/<int:course_id>')
def study_course(course_id):
    """学生学习课程 - 更新成绩"""
    if 'username' not in session or session.get('role') != 'student':
        flash('请先登录学生账户。', 'error')
        return redirect(url_for('auth.login'))

    student_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 获取当前课程注册信息
        cursor.execute("""
        SELECT score, status FROM course_enrollments 
        WHERE course_id = ? AND student_id = ?
        """, (course_id, student_id))

        enrollment = cursor.fetchone()

        if not enrollment:
            flash('您尚未注册这门课程。', 'error')
            return redirect(url_for('student.courses'))

        current_score = enrollment['score']
        current_status = enrollment['status']

        # 计算新成绩
        if current_score is None:
            # 第一次学习，随机生成成绩 (60-95之间)
            new_score = round(random.uniform(60, 95), 2)
        else:
            # 再次学习，成绩向上浮动 (1-10分)
            improvement = random.uniform(1, 10)
            new_score = min(100, round(current_score + improvement, 2))

        # 更新成绩和状态
        cursor.execute("""
        UPDATE course_enrollments 
        SET score = ?, status = 'completed', completed_at = CURRENT_TIMESTAMP
        WHERE course_id = ? AND student_id = ?
        """, (new_score, course_id, student_id))

        conn.commit()

        if current_score is None:
            flash(f'恭喜您完成了课程学习！您的成绩是: {new_score}', 'success')
        else:
            flash(f'恭喜您再次学习课程！您的成绩从 {current_score} 提升到 {new_score}', 'success')

    except Exception as e:
        conn.rollback()
        print(f"学习课程错误: {e}")
        flash('学习课程失败，请重试。', 'error')
    finally:
        conn.close()

    return redirect(url_for('student.courses'))


@student_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """学生个人资料页面"""
    if 'username' not in session or session.get('role') != 'student':
        flash('请先登录学生账户。', 'error')
        return redirect(url_for('auth.login'))

    student_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取学生详细信息
    cursor.execute("""
    SELECT username, full_name, student_id, grade, avatar, created_at
    FROM users 
    WHERE id = ?
    """, (student_id,))

    student_info = cursor.fetchone()

    # 处理表单提交
    if request.method == 'POST':
        # 修改密码
        if 'change_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # 验证当前密码
            cursor.execute("SELECT password FROM users WHERE id = ?", (student_id,))
            user = cursor.fetchone()

            if bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
                if new_password == confirm_password:
                    # 更新密码
                    new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password_hash, student_id))
                    conn.commit()
                    flash('密码修改成功！', 'success')
                else:
                    flash('新密码和确认密码不匹配。', 'error')
            else:
                flash('当前密码错误。', 'error')

        # 更新个人信息
        elif 'update_profile' in request.form:
            full_name = request.form.get('full_name')
            grade = request.form.get('grade')

            cursor.execute("""
            UPDATE users 
            SET full_name = ?, grade = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (full_name, grade, student_id))

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
                """, (avatar, student_id))

                conn.commit()

                # 更新会话中的头像
                session['avatar'] = avatar

                flash('头像更新成功！', 'success')
            else:
                flash('请选择一个头像。', 'error')

    # 重新获取学生信息（可能已更新）
    cursor.execute("""
    SELECT username, full_name, student_id, grade, avatar, created_at
    FROM users 
    WHERE id = ?
    """, (student_id,))

    student_info = cursor.fetchone()
    conn.close()

    return render_template('pages/student/profile.html',
                           student_info=student_info,
                           avatars=AVATAR_URLS)




