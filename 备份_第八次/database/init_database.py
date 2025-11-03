# database/init_database.py
import sqlite3
import os
import bcrypt
import random
from datetime import datetime, timedelta


def init_database():
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)

    # Connect to unified database
    conn = sqlite3.connect('database/komodo_hub.db')
    cursor = conn.cursor()

    # Create unified users table - 添加 last_login 列
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
        avatar TEXT DEFAULT 'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_2689977510_2663943077_fm_253_fmt_auto_app_120_f_JPEG_o2yr5a.webp',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,  -- 添加 last_login 列
        -- Teacher specific fields
        teacher_id TEXT UNIQUE,
        department TEXT,
        -- Student specific fields
        student_id TEXT UNIQUE,
        grade TEXT,
        -- Community organization specific fields
        org_name TEXT,
        contact_person TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        description TEXT,
        CHECK (role IN ('teacher', 'student', 'platform_admin', 'community_org'))
    )
    ''')

    # 检查并添加 last_login 列（如果表已存在但缺少该列）
    try:
        cursor.execute("SELECT last_login FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # 如果 last_login 列不存在，则添加它
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
        print("已添加 last_login 列到 users 表")

    # Create articles table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES users (id)
    )
    ''')

    # Create courses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES users (id)
    )
    ''')

    # Drop existing course_students table if exists
    cursor.execute("DROP TABLE IF EXISTS course_students")

    # Drop existing course_statistics table if exists
    cursor.execute("DROP TABLE IF EXISTS course_statistics")

    # Create new course-student association table with scores and status
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS course_enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        score DECIMAL(5,2),  -- Student score in this course
        status TEXT DEFAULT 'enrolled',  -- enrolled, completed, dropped
        completed_at TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES courses (id),
        FOREIGN KEY (student_id) REFERENCES users (id),
        UNIQUE(course_id, student_id)
    )
    ''')

    # Create course contents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS course_contents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        content_type TEXT DEFAULT 'lesson',  -- lesson, assignment, quiz, etc.
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES courses (id)
    )
    ''')

    # Create assignments/quiz submissions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_content_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        submission_text TEXT,
        submission_file TEXT,  -- Store file path
        score DECIMAL(5,2),
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        graded_at TIMESTAMP,
        FOREIGN KEY (course_content_id) REFERENCES course_contents (id),
        FOREIGN KEY (student_id) REFERENCES users (id)
    )
    ''')

    # Create events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        organizer_id INTEGER NOT NULL,
        event_date DATE NOT NULL,
        event_time TIME,
        location TEXT,
        max_participants INTEGER,
        current_participants INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'upcoming',  -- upcoming, ongoing, completed, cancelled
        FOREIGN KEY (organizer_id) REFERENCES users (id)
    )
    ''')

    # Create event participants table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        participation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'registered',  -- registered, attended, cancelled
        FOREIGN KEY (event_id) REFERENCES events (id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(event_id, user_id)
    )
    ''')

    # Create members table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100),
        phone VARCHAR(20),
        role VARCHAR(50) DEFAULT 'member', -- member, admin, moderator etc.
        join_date DATE,
        status VARCHAR(20) DEFAULT 'active', -- active, inactive, pending
        permissions TEXT, -- JSON formatted permission settings
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES users(id)
    )
    ''')

    # Create member groups table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS member_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES users(id)
    )
    ''')

    # Create member-group relations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS member_group_relations (
        member_id INTEGER,
        group_id INTEGER,
        PRIMARY KEY (member_id, group_id),
        FOREIGN KEY (member_id) REFERENCES members(id),
        FOREIGN KEY (group_id) REFERENCES member_groups(id)
    )
    ''')

    # 创建系统设置表和安全日志表
    create_system_settings_table(conn)
    create_security_logs_table(conn)

    # Check if users table is empty, only insert test data if empty
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        # Create initial password hash
        default_password = "123123"
        password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Preset avatar URL list
        avatar_urls = [
            'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_2689977510_2663943077_fm_253_fmt_auto_app_120_f_JPEG_o2yr5a.webp',
            'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285689/u_3767343659_1707298728_fm_253_fmt_auto_app_138_f_JPEG_bhzefm.webp',
            'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_2048403386_38307565_fm_253_fmt_auto_app_138_f_JPEG_iyjmi4.webp',
            'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_3816230571_720057739_fm_253_fmt_auto_app_120_f_JPEG_c1urfb.webp',
            'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_94149824_3403889984_fm_253_fmt_auto_app_138_f_JPEG_kqtnr7.webp',
            'https://res.cloudinary.com/dgbl5ql1v/image/upload/v1761285688/u_3348666652_2040777776_fm_253_fmt_auto_app_138_f_JPEG_a4ev92.webp'
        ]

        # Insert test user data
        test_users = [
            # Teacher user - random avatar assignment
            ('teacher@komodohub.edu', password_hash, 'teacher', 'Mr. Smith',
             random.choice(avatar_urls), 'T001', 'Biological Sciences Department', None, None, None, None,
             'teacher@komodohub.edu', '+1-555-0101', '123 Science Ave, Boston',
             'Teacher focused on Komodo dragon conservation research'),
            # Student users - random avatars
            ('student1@komodohub.edu', password_hash, 'student', 'John Davis',
             random.choice(avatar_urls), None, None, 'S001', 'Grade 3', None, None, 'student1@komodohub.edu',
             '+1-555-0102', '456 Student St, Boston', 'Student passionate about wildlife conservation'),
            ('student2@komodohub.edu', password_hash, 'student', 'Sarah Wilson',
             random.choice(avatar_urls), None, None, 'S002', 'Grade 3', None, None, 'student2@komodohub.edu',
             '+1-555-0103', '789 Learning Rd, Boston', 'Student actively participating in environmental activities'),
            ('student3@komodohub.edu', password_hash, 'student', 'Michael Brown',
             random.choice(avatar_urls), None, None, 'S003', 'Grade 4', None, None, 'student3@komodohub.edu',
             '+1-555-0104', '321 Education Blvd, Boston', 'Student with strong interest in ecology'),
            ('student4@komodohub.edu', password_hash, 'student', 'Emily Johnson',
             random.choice(avatar_urls), None, None, 'S004', 'Grade 4', None, None, 'student4@komodohub.edu',
             '+1-555-0105', '654 Knowledge Ln, Boston', 'Student aspiring to become an environmental volunteer'),
            # Platform admin - random avatar
            ('admin@komodohub.edu', password_hash, 'platform_admin', 'Platform Administrator',
             random.choice(avatar_urls), None, None, None, None, None, None, 'admin@komodohub.edu', '+1-555-0106',
             '789 Admin St, Boston', 'Komodo Hub platform administrator'),
            # Community organization - random avatar
            ('org@komodohub.org', password_hash, 'community_org', 'Green Conservation Organization',
             random.choice(avatar_urls), None, None, None, None, 'Green Conservation Organization', 'Director Wang',
             'org@komodohub.org', '+1-555-0107', '456 Conservation Tower, Boston',
             'Non-profit organization dedicated to promoting Komodo dragon conservation and environmental education')
        ]

        cursor.executemany('''
        INSERT INTO users (username, password, role, full_name, avatar, teacher_id, department, student_id, grade, org_name, contact_person, email, phone, address, description) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_users)

        # Insert test article data
        cursor.execute("SELECT id FROM users WHERE role = 'teacher'")
        teacher_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM users WHERE role = 'community_org'")
        org_id = cursor.fetchone()[0]

        test_articles = [
            ("Current Status and Research Progress in Komodo Dragon Conservation", teacher_id,
             "Komodo dragons are among the world's most precious reptiles. This article explores current conservation efforts and challenges..."),
            ("The Importance of Wildlife Conservation Education", teacher_id,
             "How to raise public awareness of wildlife conservation through education and cultivate environmental values in the next generation..."),
            ("Successful Cases of Community Participation in Ecological Conservation", org_id,
             "Introducing several successful cases where community organizations participated in local ecological conservation projects, and their experiences and achievements...")
        ]

        cursor.executemany("INSERT INTO articles (title, author_id, content) VALUES (?, ?, ?)",
                           test_articles)

        # Insert test courses
        test_courses = [
            (teacher_id, 'Introduction to Komodo Dragon Ecological Conservation',
             'Learn basic ecological knowledge and conservation methods for Komodo dragons'),
            (teacher_id, 'Wildlife Conservation Laws and Regulations',
             'Understand relevant domestic and international wildlife conservation laws and regulations'),
            (teacher_id, 'Community Conservation Project Practice',
             'Participate in actual community conservation projects to gain practical experience')
        ]

        cursor.executemany("INSERT INTO courses (teacher_id, title, description) VALUES (?, ?, ?)",
                           test_courses)

        # Insert test event data
        # Generate events with future dates
        today = datetime.now()
        test_events = [
            ("Komodo Dragon Conservation Volunteer Training",
             "Komodo dragon conservation knowledge training for community residents, learning basic protection skills and emergency response methods",
             org_id,
             (today + timedelta(days=7)).strftime('%Y-%m-%d'),
             '14:00',
             'Community Activity Center',
             50),
            ("Wildlife Conservation Awareness Day",
             "Wildlife conservation awareness event in the park, educating the public about conservation knowledge",
             org_id,
             (today + timedelta(days=14)).strftime('%Y-%m-%d'),
             '10:00',
             'City Central Park',
             100),
            ("Ecological Conservation Photography Exhibition",
             "Exhibition of photography works related to wildlife conservation, raising public conservation awareness",
             org_id,
             (today + timedelta(days=21)).strftime('%Y-%m-%d'),
             '09:00',
             'City Cultural Center',
             200)
        ]

        cursor.executemany('''
        INSERT INTO events (title, description, organizer_id, event_date, event_time, location, max_participants)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', test_events)

        # Get recently inserted course IDs and student IDs
        cursor.execute("SELECT id FROM courses WHERE teacher_id = ?", (teacher_id,))
        course_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM users WHERE role = 'student'")
        student_ids = [row[0] for row in cursor.fetchall()]

        # Assign courses to students and generate random scores
        for course_id in course_ids:
            for student_id in student_ids:
                # Generate random score (between 60-100)
                score = round(random.uniform(60, 100), 2)
                # Randomly decide if course is completed
                status = 'completed' if random.random() > 0.3 else 'enrolled'

                cursor.execute("""
                INSERT INTO course_enrollments (course_id, student_id, score, status)
                VALUES (?, ?, ?, ?)
                """, (course_id, student_id, score, status))

        # Add content to courses
        for course_id in course_ids:
            cursor.execute("SELECT title FROM courses WHERE id = ?", (course_id,))
            course_title = cursor.fetchone()[0]

            course_contents = [
                (course_id, f'{course_title} - Lesson 1', 'Course introduction and basic knowledge', 'lesson', 1),
                (course_id, f'{course_title} - Lesson 2', 'In-depth learning and case analysis', 'lesson', 2),
                (course_id, f'{course_title} - Assignment 1', 'Complete related exercises', 'assignment', 3),
                (course_id, f'{course_title} - Quiz', 'Course knowledge point test', 'quiz', 4)
            ]

            cursor.executemany("""
            INSERT INTO course_contents (course_id, title, content, content_type, order_index)
            VALUES (?, ?, ?, ?, ?)
            """, course_contents)

        # Insert test member data
        test_members = [
            (org_id, 'Volunteer Li', 'li@example.com', '+1-555-0111', 'admin', '2023-01-15', 'active',
             'Responsible for volunteer coordination'),
            (org_id, 'Enthusiast Wang', 'wang@example.com', '+1-555-0112', 'moderator', '2023-02-20', 'active',
             'Event organization lead'),
            (org_id, 'Environmentalist Zhang', 'zhang@example.com', '+1-555-0113', 'member', '2023-03-10', 'active',
             'Active participant in various activities'),
            (org_id, 'Conservationist Liu', 'liu@example.com', '+1-555-0114', 'member', '2023-04-05', 'active',
             'Komodo dragon research enthusiast'),
            (org_id, 'Ecologist Chen', 'chen@example.com', '+1-555-0115', 'member', '2023-05-12', 'inactive',
             'Currently on break'),
            (org_id, 'Green Advocate Yang', 'yang@example.com', '+1-555-0116', 'member', '2023-06-18', 'active',
             'New volunteer')
        ]

        cursor.executemany('''
        INSERT INTO members (org_id, name, email, phone, role, join_date, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_members)

        # Insert test group data
        test_groups = [
            (org_id, 'Core Team', 'Organization core management team members'),
            (org_id, 'Volunteers', 'Active volunteer members'),
            (org_id, 'Promotion Group', 'Responsible for promotion and outreach work'),
            (org_id, 'Event Group', 'Responsible for event organization and execution')
        ]

        cursor.executemany('''
        INSERT INTO member_groups (org_id, name, description)
        VALUES (?, ?, ?)
        ''', test_groups)

        # Assign members to groups
        cursor.execute("SELECT id FROM members WHERE org_id = ?", (org_id,))
        member_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM member_groups WHERE org_id = ?", (org_id,))
        group_ids = [row[0] for row in cursor.fetchall()]

        # Randomly assign groups to members
        for member_id in member_ids:
            # Assign 1-3 random groups to each member
            num_groups = random.randint(1, min(3, len(group_ids)))
            assigned_groups = random.sample(group_ids, num_groups)
            for group_id in assigned_groups:
                cursor.execute('''
                INSERT INTO member_group_relations (member_id, group_id)
                VALUES (?, ?)
                ''', (member_id, group_id))

        print("Database successfully initialized with test data")
        print("All users initial password: 123123")
        print("Teacher account: teacher@komodohub.edu")
        print(
            "Student accounts: student1@komodohub.edu, student2@komodohub.edu, student3@komodohub.edu, student4@komodohub.edu")
        print("Admin account: admin@komodohub.edu")
        print("Community organization account: org@komodohub.org")
        print("Created 3 test events")
        print("Created 6 test members and 4 groups")
    else:
        print("Database already exists, skipping initialization")

    # Commit transaction
    conn.commit()
    conn.close()


def create_system_settings_table(conn):
    """创建系统设置表"""
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT,
        description TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 插入默认设置
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

    cursor.executemany('''
    INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
    VALUES (?, ?, ?)
    ''', default_settings)

    conn.commit()


def create_security_logs_table(conn):
    """创建安全日志表"""
    cursor = conn.cursor()
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


if __name__ == "__main__":
    init_database()