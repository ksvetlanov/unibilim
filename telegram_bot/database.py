# database.py
import psycopg2
from .settings_bot import DB_HOST, DB_PASSWORD, DB_USER, DB_NAME


def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)


def get_user(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
                SELECT 'student' AS user_type, telegram_username, surname
                FROM students_student
                WHERE telegram_username = %s
                UNION
                SELECT 'professor' AS user_type, tg_username, surname
                FROM professors_professors
                WHERE tg_username = %s
            """, (username, username))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data:
            user_type, username, surname = user_data
            return {'user_type': user_type, 'username': username, 'surname': surname}
        else:
            return None
    except Exception as e:
        print("Database Error:", e)
        return None


def update_student_data(telegram_username, telegram_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE students_student
            SET telegram_id = %s
            WHERE telegram_username = %s
        """, (telegram_id, telegram_username))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Database Error:", e)


def update_professor_data(telegram_username, tg_idbot):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE professors_professors
            SET tg_idbot = %s
            WHERE tg_username = %s
        """, (tg_idbot, telegram_username))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Database Error:", e)
