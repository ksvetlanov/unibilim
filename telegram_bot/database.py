import logging
import asyncpg
from .settings_bot import DB_HOST, DB_USER, DB_NAME
import datetime
import pytz
import subprocess


class DataBase:
    def __init__(self, db_host, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.pool = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )

    async def execute_query(self, query, *args):
        try:
            async with self.pool.acquire() as connection:
                result = await connection.fetch(query, *args)
                return result
        except Exception as e:
            logging.info(f"Database Error: {e}")
            return None

    async def backup_db(self):
        open('backup_file.sql', 'w').close()

        backup_file = 'backup_file.sql'

        try:
            pg_dump_path = r'C:\Program Files\PostgreSQL\15\bin\pg_dump.exe'
            subprocess.run([
                f'{pg_dump_path}',
                '-h', DB_HOST,
                '-U', DB_USER,
                '-d', DB_NAME,
                '-f', backup_file,
            ])
            return backup_file
        except Exception as e:
            logging.info(f"Произошла ошибка при создании резервной копии: {e}")
            return None


class UserManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def get_user(self, telegram_username):
        try:
            query = """
                SELECT 'student' AS user_type, id, telegram_username, surname, user_id
                FROM students_student
                WHERE telegram_username = $1
                UNION
                SELECT 'professor' AS user_type, id, tg_username, surname, user_id
                FROM professors_professors
                WHERE tg_username = $2
            """

            data = await self.db_manager.execute_query(query, telegram_username, telegram_username)

            if data:
                user_type, user_id, telegram_username, surname, user__id = data[0]
                user_data = {
                    'user_type': user_type,
                    'id': user_id,
                    'username': telegram_username,
                    'surname': surname,
                    'user__id': user__id
                }

                return user_data
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def get_token(self, user__id):
        try:
            query = """
                SELECT auth_token.key FROM authtoken_token AS auth_token 
                JOIN auth_user ON auth_token.user_id = auth_user.id 
                WHERE auth_user.id = $1
            """

            data = await self.db_manager.execute_query(query, user__id)

            if data:
                return data[0][0]
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def get_chat_id(self, telegram_username):
        try:
            query = """
                SELECT telegram_id
                FROM (
                    SELECT telegram_username AS username, telegram_id
                    FROM students_student
                    UNION
                    SELECT tg_username AS username, tg_idbot AS telegram_id
                    FROM professors_professors
                ) AS combined_data
                WHERE username = $1
            """
            data = await self.db_manager.execute_query(query, telegram_username)

            if data:
                return data[0][0]
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def create_reset_password_code(self, user__id, code):
        try:
            query = """
                INSERT INTO accounts_passwordresetcode (user_id, code) VALUES ($1, $2)
            """

            await self.db_manager.execute_query(query, user__id, code)
            logging.info('Create password reset code successful')
            return True

        except Exception as e:
            logging.info("Database Error:", e)
            return False

    async def get_reset_password_code(self, user_id):
        try:
            query = """
                SELECT code FROM accounts_passwordresetcode
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 1
            """
            result = await self.db_manager.execute_query(query, user_id)
            if result:
                return result[0]['code']
            else:
                return None
        except Exception as e:
            logging.info("Database Error:", e)


class ProfessorManager(UserManager):
    def __init__(self, db_manager):
        super().__init__(db_manager)

    async def get_data(self, telegram_username):
        try:
            query = """
                SELECT id, tg_username, tg_idbot
                FROM professors_professors
                WHERE tg_username = $1
            """

            data = await self.db_manager.execute_query(query, telegram_username)

            user_type = 'professor'

            if data:
                return {'id': data[0][0], 'username': data[0][1], 'chat_id': data[0][2], 'user_type': user_type}
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def get_meetings(self, professor_id):
        try:
            query = """
                SELECT *
                FROM meetings_meetings
                WHERE professor_id = $1
            """

            data = await self.db_manager.execute_query(query, professor_id)
            if data:
                return data
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def get_today_meetings(self, professor_id, start_date, end_date):
        try:
            query = """
                SELECT datetime, student_id
                FROM meetings_meetings
                WHERE professor_id = $1 AND DATE(datetime) BETWEEN $2 AND $3;
            """

            data = await self.db_manager.execute_query(query, professor_id, start_date, end_date)
            if data:
                return data
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def update_chat_id(self, telegram_username, chat_id):
        try:
            query = """
                UPDATE professors_professors
                SET tg_idbot = $2
                WHERE tg_username = $1
            """

            await self.db_manager.execute_query(query, telegram_username, str(chat_id))
            logging.info("Update chat_id successful")
            return True

        except Exception as e:
            logging.info("Database Error:", e)
            return False

    async def get_professor_by_id(self, professor_id):
        try:
            query = """
                SELECT id, tg_username, tg_idbot, user_id
                FROM professors_professors
                WHERE id = $1;
            """

            data = await self.db_manager.execute_query(query, professor_id)

            if data:
                professor_data = {
                    'id': data[0][0],
                    'username': data[0][1],
                    'chat_id': data[0][2],
                    'user_id': data[0][3]
                }

                return professor_data
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)


class StudentManager(UserManager):
    def __init__(self, db_manager):
        super().__init__(db_manager)

    async def get_meetings(self, student_id):
        try:
            query = """
                SELECT *
                FROM meetings_meetings
                WHERE student_id = $1
            """

            data = await self.db_manager.execute_query(query, student_id)

            return data

        except Exception as e:
            logging.info("Database Error:", e)

    async def update_chat_id(self, telegram_username, chat_id):
        try:
            query = """
                UPDATE students_student
                SET telegram_id = $2
                WHERE telegram_username = $1
            """

            await self.db_manager.execute_query(query, telegram_username, str(chat_id))
            logging.info("Update chat_id successful")
            return True

        except Exception as e:
            logging.info("Database Error:", e)
            return False

    async def get_username(self, student_id):
        try:
            query = """
                SELECT telegram_username
                FROM students_student
                WHERE id = $1;
            """

            data = await self.db_manager.execute_query(query, student_id)

            if data:
                return data[0][0]
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def get_info(self, student_id):
        try:
            query = """
                SELECT firstname, surname
                FROM students_student
                WHERE id = $1;
            """

            data = await self.db_manager.execute_query(query, student_id)

            if data:
                student_info = {'full_name': f"{data[0][0]} {data[0][1]}"}
                return student_info
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)


class MeetingManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def update_status(self, meeting_id, new_status):
        try:
            query = """
                UPDATE meetings_meetings
                SET status = $1
                WHERE id = $2
            """

            await self.db_manager.execute_query(query, new_status, meeting_id)
            logging.info("Update status successful")
            return True

        except Exception as e:
            logging.info("Database Error:", e)
            return False

    async def sorting(self, meetings):
        try:
            current_time_utc = datetime.datetime.now(pytz.utc)
            current_time_utc += datetime.timedelta(hours=6)
            valid_meetings = [meeting for meeting in meetings if meeting[1] > current_time_utc]
            sorted_meetings = sorted(valid_meetings, key=lambda x: abs(x[1] - current_time_utc))

            if sorted_meetings:
                return{
                    'id': sorted_meetings[0]['id'],
                    'datetime': sorted_meetings[0]['datetime'],
                    'jitsiLink': sorted_meetings[0]['jitsiLink'],
                    'subject': sorted_meetings[0]['subject'],
                    'day_of_week': sorted_meetings[0]['day_of_week'],
                    'status': sorted_meetings[0]['status'],
                    'duration': sorted_meetings[0]['duration'],
                    'professor_id': sorted_meetings[0]['professor_id'],
                    'student_id': sorted_meetings[0]['student_id'],
                }
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def create_meetings_confirmation(self, chat_id, username, appointed_time, duration, status, meeting_id,
                                           professor_id, confirmation_attempts):
        try:
            query = """
                INSERT INTO meetings_meetingsconfirmation (chat_id, username, appointed_time, duration, status, meeting_id, professor_id, confirmation_attempts)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
            """

            await self.db_manager.execute_query(query, chat_id, username, appointed_time, duration, status, meeting_id,
                                                professor_id, confirmation_attempts)

            logging.info("MeetingsConfirmation created successfully")
            return True

        except Exception as e:
            logging.info("Database Error:", e)
            return False

    async def get_unsent_meetings_confirmation(self):
        try:
            query = """
                SELECT id, chat_id, username, appointed_time, duration, status, meeting_id, professor_id
                FROM meetings_meetingsconfirmation
                WHERE status = 'DID NOT SENT';
            """

            data = await self.db_manager.execute_query(query)

            unsent_meetings_confirmation = []
            for row in data:
                meetings_confirmation_data = {
                    'id': row[0],
                    'chat_id': row[1],
                    'username': row[2],
                    'appointed_time': row[3],
                    'duration': row[4],
                    'status': row[5],
                    'meeting_id': row[6],
                    'professor_id': row[7],
                }
                unsent_meetings_confirmation.append(meetings_confirmation_data)

            return unsent_meetings_confirmation

        except Exception as e:
            logging.info("Database Error:", e)

    async def get_meeting_confirmation_id(self, meeting_id):
        try:
            query = """
                SELECT id
                FROM meetings_meetingsconfirmation
                WHERE meeting_id = $1
            """
            result = await self.db_manager.execute_query(query, meeting_id)

            return result[0]['id'] if result else None

        except Exception as e:
            logging.info(f"Database Error: {e}")
            return None

    async def update_status_confirmation(self, confirmation_id, new_status):
        try:
            query = """
                UPDATE meetings_meetingsconfirmation
                SET status = $1
                WHERE id = $2
            """

            await self.db_manager.execute_query(query, new_status, confirmation_id)
            logging.info("Update confirmation status successful")
            return True

        except Exception as e:
            logging.info("Database Error:", e)
            return False

    async def get_new_meeting(self):
        try:
            query = """
                SELECT id, professor_id
                FROM payments_payments
                WHERE status_new_meeting = 'DID NOT SENT'
                AND status = 'COMPLETED';
            """

            data = await self.db_manager.execute_query(query)

            result = []
            for row in data:
                result.append({
                    'id': row[0],
                    'professor_id': row[1],
                })

            return result

        except Exception as e:
            logging.info("Database Error:", e)

    async def update_status_payments(self, payment_id, new_status):
        try:
            query = """
                UPDATE payments_payments
                SET status_new_meeting = $1
                WHERE id = $2
            """

            await self.db_manager.execute_query(query, new_status, payment_id)
            logging.info("Update payments status successful")
            return True

        except Exception as e:
            logging.info("Database Error:", e)
            return False

    async def get_meeting_by_id(self, meeting_id):
        try:
            query = """
                SELECT student_id, professor_id
                FROM meetings_meetings
                WHERE id = $1;
            """

            data = await self.db_manager.execute_query(query, meeting_id)

            if data:
                row = data[0]
                result = {
                    'student_id': row[0],
                    'professor_id': row[1],
                }
                return result
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def get_confirmation_data(self, confirmation_id):
        try:
            query = """
                SELECT confirmation_attempts, duration
                FROM meetings_meetingsconfirmation
                WHERE id = $1;
            """

            data = await self.db_manager.execute_query(query, confirmation_id)

            if data:
                confirmation_data = {
                    'confirmation_attempts': data[0][0],
                    'duration': data[0][1],

                }
                return confirmation_data
            else:
                return None

        except Exception as e:
            logging.info("Database Error:", e)

    async def update_meeting_confirmation(self, confirmation_id, new_duration, new_confirmation_attempts):
        try:
            query = """
                UPDATE meetings_meetingsconfirmation
                SET duration = $1, confirmation_attempts = $2
                WHERE id = $3;
            """

            await self.db_manager.execute_query(query, new_duration, new_confirmation_attempts, confirmation_id)
            logging.info("Update meeting_confirmation data successful")
            return True

        except Exception as e:
            logging.error(f"Database Error: {e}")
            return False











