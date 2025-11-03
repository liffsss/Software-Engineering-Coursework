# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.models import get_db_connection
import bcrypt

auth_bp = Blueprint('auth', __name__)

# 预设头像URL列表
AVATAR_URLS = [
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_2689977510_2663943077_fm_253_fmt_auto_app_120_f_JPEG_o2yr5a.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285689/u_3767343659_1707298728_fm_253_fmt_auto_app_138_f_JPEG_bhzefm.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_2048403386_38307565_fm_253_fmt_auto_app_138_f_JPEG_iyjmi4.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_3816230571_720057739_fm_253_fmt_auto_app_120_f_JPEG_c1urfb.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_94149824_3403889984_fm_253_fmt_auto_app_138_f_JPEG_kqtnr7.webp',
    'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_3348666652_2040777776_fm_253_fmt_auto_app_138_f_JPEG_a4ev92.webp'
]


def verify_password(stored_password, provided_password):
    """验证密码函数 - 使用bcrypt验证"""
    try:
        # 使用bcrypt验证密码
        return bcrypt.checkpw(
            provided_password.encode('utf-8'),
            stored_password.encode('utf-8')
        )
    except Exception as e:
        print(f"密码验证错误: {e}")
        # 如果bcrypt验证失败，尝试其他方法
        try:
            # 检查是否是旧格式的哈希 (哈希值:盐值)
            if ':' in stored_password and len(stored_password.split(':')) == 2:
                import hashlib
                stored_hash, salt = stored_password.split(':')
                new_hash = hashlib.pbkdf2_hmac(
                    'sha256',
                    provided_password.encode('utf-8'),
                    salt.encode('utf-8'),
                    100000
                ).hex()
                return stored_hash == new_hash
            else:
                # 可能是旧数据库的明文密码，直接比较
                return stored_password == provided_password
        except:
            return False


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询用户
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            # 验证密码
            if verify_password(user['password'], password):
                # 更新最后登录时间
                from datetime import datetime
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), user['id'])
                )
                conn.commit()

                # 设置会话
                session['username'] = username
                session['role'] = user['role']
                session['user_id'] = user['id']
                session['full_name'] = user['full_name'] if user['full_name'] is not None else username
                session['avatar'] = user['avatar'] if user['avatar'] is not None else AVATAR_URLS[0]

                # 根据角色重定向
                if user['role'] == 'teacher':
                    return redirect(url_for('teacher.dashboard'))
                elif user['role'] == 'student':
                    return redirect(url_for('student.dashboard'))
                elif user['role'] == 'community_org':
                    return redirect(url_for('community.dashboard'))
                elif user['role'] == 'platform_admin':
                    return redirect(url_for('admin.dashboard'))
            else:
                flash('用户名或密码错误，请重试。', 'error')
        else:
            flash('用户名或密码错误，请重试。', 'error')

        conn.close()

    return render_template('pages/login/login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('user_id', None)
    session.pop('full_name', None)
    session.pop('avatar', None)
    flash('您已成功退出登录。', 'success')
    return redirect(url_for('auth.login'))