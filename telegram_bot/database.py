#database.py
from datetime import datetime, timezone

import psycopg2
from telegram_bot.settings_bot import DB_HOST, DB_PASSWORD, DB_USER, DB_NAME


def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)


def get_user(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 'student' AS user_type, id, telegram_username, surname
            FROM students_student
            WHERE telegram_username = %s
            UNION
            SELECT 'professor' AS user_type, id, tg_username, surname
            FROM professors_professors
            WHERE tg_username = %s
        """, (username, username))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data:
            user_type, user_id, username, surname = user_data
            return {'user_type': user_type, 'id': user_id, 'username': username, 'surname': surname}
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


def get_meeting_professors(professor_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT *
        FROM meetings_meetings
        WHERE professor_id = %s
        """
        cursor.execute(query, (professor_id,))

        meetings = cursor.fetchall()

        cursor.close()
        conn.close()

        return meetings

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


def get_meeting_students(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()


        query = """
        SELECT *
        FROM meetings_meetings
        WHERE student_id = %s
        """
        cursor.execute(query, (student_id,))

        meetings = cursor.fetchall()

        cursor.close()
        conn.close()

        return meetings

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


def get_telegram_id(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT telegram_id
            FROM (
                SELECT telegram_username AS username, telegram_id
                FROM students_student
                UNION
                SELECT tg_username AS username, tg_idbot AS telegram_id
                FROM professors_professors
            ) AS combined_data
            WHERE username = %s
        """, (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data:
            telegram_id = user_data[0]
            return telegram_id
        else:
            return None
    except Exception as e:
        print("Database Error:", e)
        return None


def sorted_meetings(meetings):

    current_time = datetime.now(timezone.utc)

    sort_meetings = sorted(meetings, key=lambda x: abs(x[1] - current_time))
    return sort_meetings






