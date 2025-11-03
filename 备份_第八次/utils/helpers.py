# utils/helpers.py
import time
from flask import flash
from database.models import get_db_connection


def add_student(teacher_id, full_name, email):
    """添加学生"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        username = email.split('@')[0] if email else f"student{int(time.time())}"
        password = "123456"

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, 'student')",
            (username, password)
        )
        user_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO students (user_id, full_name, email) VALUES (?, ?, ?)",
            (user_id, full_name, email)
        )
        student_id = cursor.lastrowid

        cursor.execute("SELECT id FROM courses WHERE teacher_id = ?", (teacher_id,))
        courses = cursor.fetchall()

        for course in courses:
            cursor.execute(
                "INSERT INTO course_students (course_id, student_id) VALUES (?, ?)",
                (course['id'], student_id)
            )

        conn.commit()
        flash('学生添加成功！', 'success')
        return True
    except Exception as e:
        conn.rollback()
        flash(f'添加学生失败: {str(e)}', 'error')
        return False
    finally:
        conn.close()


def delete_student(student_id):
    """删除学生"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM course_students WHERE student_id = ?", (student_id,))

        cursor.execute("SELECT user_id FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()

        if student:
            user_id = student['user_id']
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

        conn.commit()
        flash('学生删除成功！', 'success')
        return True
    except Exception as e:
        conn.rollback()
        flash(f'删除学生失败: {str(e)}', 'error')
        return False
    finally:
        conn.close()