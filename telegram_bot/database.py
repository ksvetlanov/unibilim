import psycopg2
from .settings_bot import DB_HOST, DB_PASSWORD, DB_USER, DB_NAME
import datetime
import pytz


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


def get_professor_data(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tg_username, tg_idbot
            FROM professors_professors
            WHERE tg_username = %s
        """, (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        user_type = 'professor'
        # Проверяем, найдены ли данные
        if user_data:
            # Создаем словарь с именем пользователя и его данными
            user_dict = {
                'id': user_data[0],
                'username': user_data[1],
                'chat_id': user_data[2],
                'user_type': user_type,
            }
            return user_dict
        else:
            return None
    except Exception as e:
        print(f"Ошибка при выполнении SQL-запроса: {str(e)}")
        return None


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


def update_meeting_status(meeting_id, new_status):
    try:
        conn = get_db_connection()  # Получите соединение с базой данных
        cursor = conn.cursor()

        sql_query = """
            UPDATE meetings_meetings
            SET status = %s
            WHERE id = %s
        """
        cursor.execute(sql_query, (new_status, meeting_id))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Database Error:", e)


def sort_meetings(meetings):
    current_time_utc = datetime.datetime.now(pytz.utc)
    current_time_utc += datetime.timedelta(hours=6)
    valid_meetings = [meeting for meeting in meetings if meeting[1] > current_time_utc]
    sorted_meetings = sorted(valid_meetings, key=lambda x: abs(x[1] - current_time_utc))
    for meeting in sorted_meetings:
        return meeting

