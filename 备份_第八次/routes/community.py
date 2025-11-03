# routes/community.py
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from database.models import get_db_connection, get_articles, get_community_events, create_event, delete_event

community_bp = Blueprint('community', __name__, url_prefix='/community')


@community_bp.route('/dashboard')
def dashboard():
    if 'role' in session and session['role'] == 'community_org':
        articles = get_articles()
        events = get_community_events(session['user_id'])

        # 获取社区组织的基本信息
        conn = get_db_connection()
        cursor = conn.cursor()

        # 修改这里：获取所有已发布文章的数量，而不仅仅是当前用户的
        cursor.execute("SELECT COUNT(*) FROM articles")
        article_count = cursor.fetchone()[0]

        # 获取活动数量（保持原样，只计算当前用户的活动）
        cursor.execute("SELECT COUNT(*) FROM events WHERE organizer_id = ?", (session['user_id'],))
        event_count = cursor.fetchone()[0]

        # 新增：获取成员数量
        cursor.execute("SELECT COUNT(*) FROM members WHERE org_id = ?", (session['user_id'],))
        member_count = cursor.fetchone()[0]

        # 获取社区组织信息
        cursor.execute("SELECT org_name, contact_person FROM users WHERE id = ?", (session['user_id'],))
        org_info = cursor.fetchone()

        conn.close()

        return render_template(
            'pages/community/community.html',
            username=session['username'],
            articles=articles,
            events=events,
            article_count=article_count,
            event_count=event_count,
            member_count=member_count,  # 新增：传递成员数量
            org_name=org_info['org_name'] if org_info else '',
            contact_person=org_info['contact_person'] if org_info else ''
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/articles')
def manage_articles():
    if 'role' in session and session['role'] == 'community_org':
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取所有文章，而不仅仅是当前社区组织发布的文章
        cursor.execute('''
        SELECT a.*, u.full_name, u.org_name 
        FROM articles a 
        JOIN users u ON a.author_id = u.id 
        ORDER BY a.created_at DESC
        ''')
        articles = cursor.fetchall()

        conn.close()

        return render_template(
            'pages/community/manage_articles.html',
            username=session['username'],
            articles=articles
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/articles/create', methods=['GET', 'POST'])
def create_article():
    if 'role' in session and session['role'] == 'community_org':
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')

            if title and content:
                conn = get_db_connection()
                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "INSERT INTO articles (title, author_id, content) VALUES (?, ?, ?)",
                        (title, session['user_id'], content)
                    )
                    conn.commit()
                    flash('文章发布成功！', 'success')
                    return redirect(url_for('community.manage_articles'))
                except Exception as e:
                    flash(f'发布文章失败: {str(e)}', 'error')
                finally:
                    conn.close()
            else:
                flash('请填写标题和内容', 'error')

        return render_template(
            'pages/community/create_article.html',
            username=session['username']
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/articles/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    if 'role' in session and session['role'] == 'community_org':
        conn = get_db_connection()
        cursor = conn.cursor()

        # 确保只能编辑所有文章
        cursor.execute('''
        SELECT a.*, u.full_name, u.org_name 
        FROM articles a 
        JOIN users u ON a.author_id = u.id 
        WHERE a.id = ?
        ''', (article_id,))
        article = cursor.fetchone()

        if not article:
            flash('文章不存在', 'error')
            return redirect(url_for('community.manage_articles'))

        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')

            if title and content:
                try:
                    cursor.execute(
                        "UPDATE articles SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (title, content, article_id)
                    )
                    conn.commit()
                    flash('文章更新成功！', 'success')
                    return redirect(url_for('community.manage_articles'))
                except Exception as e:
                    flash(f'更新文章失败: {str(e)}', 'error')
            else:
                flash('请填写标题和内容', 'error')

        conn.close()
        return render_template(
            'pages/community/edit_article.html',
            username=session['username'],
            article=article
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/articles/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    if 'role' in session and session['role'] == 'community_org':
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 确保可以删除所有文章
            cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
            conn.commit()
            flash('文章删除成功！', 'success')
        except Exception as e:
            flash(f'删除文章失败: {str(e)}', 'error')
        finally:
            conn.close()

        return redirect(url_for('community.manage_articles'))
    return redirect(url_for('auth.login'))


@community_bp.route('/profile')
def profile():
    if 'role' in session and session['role'] == 'community_org':
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()

        # 获取文章总数（所有文章）
        cursor.execute("SELECT COUNT(*) FROM articles")
        article_count = cursor.fetchone()[0]

        # 获取活动总数（当前用户的活动）
        cursor.execute("SELECT COUNT(*) FROM events WHERE organizer_id = ?", (session['user_id'],))
        event_count = cursor.fetchone()[0]

        # 获取成员总数
        cursor.execute("SELECT COUNT(*) FROM members WHERE org_id = ?", (session['user_id'],))
        member_count = cursor.fetchone()[0]

        conn.close()

        return render_template(
            'pages/community/profile.html',
            username=session['username'],
            user=user,
            article_count=article_count,
            event_count=event_count,
            member_count=member_count  # 取消注释并传递成员数量
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/members')
def manage_members():
    if 'role' in session and session['role'] == 'community_org':
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取所有成员及其分组信息
        cursor.execute('''
        SELECT m.*, 
               GROUP_CONCAT(mg.id) as group_ids,
               GROUP_CONCAT(mg.name) as group_names,
               GROUP_CONCAT(mg.description) as group_descriptions
        FROM members m 
        LEFT JOIN member_group_relations mgr ON m.id = mgr.member_id
        LEFT JOIN member_groups mg ON mgr.group_id = mg.id
        WHERE m.org_id = ?
        GROUP BY m.id
        ORDER BY m.created_at DESC
        ''', (session['user_id'],))
        members = cursor.fetchall()

        # 获取所有分组
        cursor.execute('SELECT * FROM member_groups WHERE org_id = ? ORDER BY name', (session['user_id'],))
        groups = cursor.fetchall()

        # 获取成员统计
        cursor.execute('SELECT COUNT(*) FROM members WHERE org_id = ? AND status = "active"', (session['user_id'],))
        active_members = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM members WHERE org_id = ? AND status = "inactive"', (session['user_id'],))
        inactive_members = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM members WHERE org_id = ? AND role = "admin"', (session['user_id'],))
        admin_members = cursor.fetchone()[0]

        # 按分组组织成员
        grouped_members = {}
        ungrouped_members = []

        # 初始化分组字典
        for group in groups:
            grouped_members[group['id']] = {
                'group_info': group,
                'members': []
            }

        # 分配成员到分组
        for member in members:
            if member['group_ids']:
                group_ids = [int(id) for id in member['group_ids'].split(',')] if member['group_ids'] else []
                for group_id in group_ids:
                    if group_id in grouped_members:
                        grouped_members[group_id]['members'].append(member)
            else:
                ungrouped_members.append(member)

        conn.close()

        return render_template(
            'pages/community/manage_members.html',
            username=session['username'],
            members=members,
            groups=groups,
            grouped_members=grouped_members,
            ungrouped_members=ungrouped_members,
            active_members=active_members,
            inactive_members=inactive_members,
            admin_members=admin_members
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/members/create', methods=['GET', 'POST'])
def create_member():
    """创建新成员"""
    if 'role' in session and session['role'] == 'community_org':
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            role = request.form.get('role', 'member')
            join_date = request.form.get('join_date')
            status = request.form.get('status', 'active')
            notes = request.form.get('notes')

            if name:
                conn = get_db_connection()
                cursor = conn.cursor()

                try:
                    cursor.execute('''
                    INSERT INTO members (org_id, name, email, phone, role, join_date, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (session['user_id'], name, email, phone, role, join_date, status, notes))
                    conn.commit()
                    flash('成员添加成功！', 'success')
                    return redirect(url_for('community.manage_members'))
                except Exception as e:
                    flash(f'添加成员失败: {str(e)}', 'error')
                finally:
                    conn.close()
            else:
                flash('请填写成员姓名', 'error')

        return render_template(
            'pages/community/create_member.html',
            username=session['username']
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/members/edit/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    """编辑成员"""
    if 'role' in session and session['role'] == 'community_org':
        conn = get_db_connection()
        cursor = conn.cursor()

        # 确保只能编辑自己组织的成员
        cursor.execute('SELECT * FROM members WHERE id = ? AND org_id = ?', (member_id, session['user_id']))
        member = cursor.fetchone()

        if not member:
            flash('成员不存在或无权编辑', 'error')
            return redirect(url_for('community.manage_members'))

        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            role = request.form.get('role')
            join_date = request.form.get('join_date')
            status = request.form.get('status')
            notes = request.form.get('notes')

            if name:
                try:
                    cursor.execute('''
                    UPDATE members 
                    SET name = ?, email = ?, phone = ?, role = ?, join_date = ?, status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND org_id = ?
                    ''', (name, email, phone, role, join_date, status, notes, member_id, session['user_id']))
                    conn.commit()
                    flash('成员信息更新成功！', 'success')
                    return redirect(url_for('community.manage_members'))
                except Exception as e:
                    flash(f'更新成员信息失败: {str(e)}', 'error')
            else:
                flash('请填写成员姓名', 'error')

        conn.close()
        return render_template(
            'pages/community/edit_member.html',
            username=session['username'],
            member=member
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/members/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    """删除成员"""
    if 'role' in session and session['role'] == 'community_org':
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 确保只能删除自己组织的成员
            cursor.execute('DELETE FROM members WHERE id = ? AND org_id = ?', (member_id, session['user_id']))
            conn.commit()
            flash('成员删除成功！', 'success')
        except Exception as e:
            flash(f'删除成员失败: {str(e)}', 'error')
        finally:
            conn.close()

        return redirect(url_for('community.manage_members'))
    return redirect(url_for('auth.login'))


@community_bp.route('/member_groups/create', methods=['POST'])
def create_member_group():
    """创建成员分组"""
    if 'role' in session and session['role'] == 'community_org':
        name = request.form.get('name')
        description = request.form.get('description')

        if name:
            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                cursor.execute('''
                INSERT INTO member_groups (org_id, name, description)
                VALUES (?, ?, ?)
                ''', (session['user_id'], name, description))
                conn.commit()
                flash('分组创建成功！', 'success')
            except Exception as e:
                flash(f'创建分组失败: {str(e)}', 'error')
            finally:
                conn.close()
        else:
            flash('请填写分组名称', 'error')

        return redirect(url_for('community.manage_members'))
    return redirect(url_for('auth.login'))


# 活动管理路由
@community_bp.route('/events')
def manage_events():
    if 'role' in session and session['role'] == 'community_org':
        events = get_community_events(session['user_id'])

        return render_template(
            'pages/community/manage_events.html',
            username=session['username'],
            events=events
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/events/create', methods=['GET', 'POST'])
def create_event_route():
    if 'role' in session and session['role'] == 'community_org':
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            event_date = request.form.get('event_date')
            event_time = request.form.get('event_time')
            location = request.form.get('location')
            max_participants = request.form.get('max_participants')

            if title and description and event_date:
                event_id = create_event(
                    title=title,
                    description=description,
                    organizer_id=session['user_id'],
                    event_date=event_date,
                    event_time=event_time,
                    location=location,
                    max_participants=int(max_participants) if max_participants else None
                )

                if event_id:
                    flash('活动创建成功！', 'success')
                    return redirect(url_for('community.manage_events'))
                else:
                    flash('创建活动失败，请重试', 'error')
            else:
                flash('请填写必填字段', 'error')

        return render_template(
            'pages/community/create_event.html',
            username=session['username']
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/events/delete/<int:event_id>', methods=['POST'])
def delete_event_route(event_id):
    if 'role' in session and session['role'] == 'community_org':
        success = delete_event(event_id, session['user_id'])
        if success:
            flash('活动删除成功！', 'success')
        else:
            flash('删除活动失败或无权删除', 'error')

        return redirect(url_for('community.manage_events'))
    return redirect(url_for('auth.login'))


@community_bp.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event_route(event_id):
    if 'role' in session and session['role'] == 'community_org':
        conn = get_db_connection()
        cursor = conn.cursor()

        # 确保只能编辑自己的活动
        cursor.execute('SELECT * FROM events WHERE id = ? AND organizer_id = ?',
                       (event_id, session['user_id']))
        event = cursor.fetchone()

        if not event:
            flash('活动不存在或无权编辑', 'error')
            return redirect(url_for('community.manage_events'))

        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            event_date = request.form.get('event_date')
            event_time = request.form.get('event_time')
            location = request.form.get('location')
            max_participants = request.form.get('max_participants')
            status = request.form.get('status')

            if title and description and event_date:
                try:
                    cursor.execute('''
                    UPDATE events 
                    SET title = ?, description = ?, event_date = ?, event_time = ?, 
                        location = ?, max_participants = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND organizer_id = ?
                    ''', (title, description, event_date, event_time, location,
                          max_participants, status, event_id, session['user_id']))
                    conn.commit()
                    flash('活动更新成功！', 'success')
                    return redirect(url_for('community.manage_events'))
                except Exception as e:
                    flash(f'更新活动失败: {str(e)}', 'error')
            else:
                flash('请填写必填字段', 'error')

        conn.close()
        return render_template(
            'pages/community/edit_event.html',
            username=session['username'],
            event=event
        )
    return redirect(url_for('auth.login'))


@community_bp.route('/members/<int:member_id>/assign_group', methods=['POST'])
def assign_member_to_group(member_id):
    """将成员分配到分组"""
    if 'role' in session and session['role'] == 'community_org':
        group_id = request.form.get('group_id')

        if group_id:
            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                # 先检查成员是否已经在该分组中
                cursor.execute('''
                SELECT * FROM member_group_relations 
                WHERE member_id = ? AND group_id = ?
                ''', (member_id, group_id))
                existing_relation = cursor.fetchone()

                if not existing_relation:
                    # 将成员添加到分组
                    cursor.execute('''
                    INSERT INTO member_group_relations (member_id, group_id)
                    VALUES (?, ?)
                    ''', (member_id, group_id))
                    conn.commit()
                    flash('成员已成功分配到分组！', 'success')
                else:
                    flash('成员已在该分组中', 'info')

            except Exception as e:
                flash(f'分配成员到分组失败: {str(e)}', 'error')
            finally:
                conn.close()
        else:
            flash('请选择分组', 'error')

        return redirect(url_for('community.manage_members'))
    return redirect(url_for('auth.login'))


@community_bp.route('/members/<int:member_id>/remove_from_group/<int:group_id>', methods=['POST'])
def remove_member_from_group(member_id, group_id):
    """将成员从分组中移除"""
    if 'role' in session and session['role'] == 'community_org':
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 确保只能操作自己组织的成员
            cursor.execute('''
            DELETE FROM member_group_relations 
            WHERE member_id = ? AND group_id = ?
            AND member_id IN (SELECT id FROM members WHERE org_id = ?)
            ''', (member_id, group_id, session['user_id']))
            conn.commit()
            flash('成员已从分组中移除！', 'success')
        except Exception as e:
            flash(f'移除成员失败: {str(e)}', 'error')
        finally:
            conn.close()

        return redirect(url_for('community.manage_members'))
    return redirect(url_for('auth.login'))