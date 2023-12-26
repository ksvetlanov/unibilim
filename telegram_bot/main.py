import datetime
import asyncio
import logging
import aiocron
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import executor
from .settings_bot import TOKEN, DB_HOST, DB_PASSWORD, DB_USER, DB_NAME
from .database import UserManager, StudentManager, ProfessorManager, MeetingManager, DataBase
from .command_handler import CommandHandler
from .message_handler import MessageHandler


class MyState(StatesGroup):
    backup_password = State()
    copy_file_password = State()
    check_file_name = State()
    file_name_list_password = State()
    password_reset_code = State()
    password_reset = State()
    handle_confirmation_response = State()


class MainBotServices:
    pass


class MainBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self.dp.middleware.setup(LoggingMiddleware())
        self.db = DataBase(db_host=DB_HOST, db_password=DB_PASSWORD, db_name=DB_NAME, db_user=DB_USER)
        self.user_db_manager = UserManager(self.db)
        self.professor_db_manager = ProfessorManager(self.db)
        self.student_db_manager = StudentManager(self.db)
        self.meeting_db_manager = MeetingManager(self.db)
        self.main_bot_services = MainBotServices()
        self.my_state = MyState()
        self.user_tasks = {}
        self.meeting_not_marked = {}
        self.command_handler = CommandHandler(
                self.bot,
                self.dp,
                self.db,
                self.user_db_manager,
                self.professor_db_manager,
                self.student_db_manager,
                self.meeting_db_manager,
                self.my_state
            )
        self.message_handler = MessageHandler(
                self.bot,
                self.dp,
                self.db,
                self.user_db_manager,
                self.professor_db_manager,
                self.student_db_manager,
                self.meeting_db_manager,
                self.command_handler,
                self.my_state
            )

    async def stop_user_task(self, username):
        if username in self.user_tasks:
            task = self.user_tasks.pop(username)
            task.cancel()

    async def sending_confirmation_message(self, chat_id, username, meeting_appointed_time, meeting_duration, meeting_id):
        try:
            kyrgyzstan_timezone = pytz.timezone('Asia/Bishkek')
            current_time_kyrgyzstan = datetime.datetime.now(kyrgyzstan_timezone)
            meeting_time_kyrgyzstan = meeting_appointed_time - datetime.timedelta(hours=6)
            meeting_end_time = meeting_time_kyrgyzstan + meeting_duration
            log_meeting_time = meeting_end_time + datetime.timedelta(hours=6)
            time_difference = meeting_end_time - current_time_kyrgyzstan
            logging.info(f'Встреча закончится в : {log_meeting_time}\nОпрос придет пользователю {username} через : {time_difference}')
            time_difference_minutes = (meeting_end_time - current_time_kyrgyzstan).total_seconds() / 60

            if 0 < time_difference_minutes <= 1:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
                markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))

                await self.bot.send_message(chat_id, "Прошла ли встреча?", reply_markup=markup)
                logging.info(f"Опрос отправлен пользователю {username}")

                self.message_handler.user_data['current_state'] = 'waiting_confirmation'

            elif time_difference_minutes < 0:
                self.meeting_not_marked[username] = {
                    'username': username,
                    'chat_id': chat_id,
                    'meeting_id': meeting_id
                }
                logging.info(f'Пользователь {username} не подтвердил встречу')

        except Exception as e:
            logging.info(f"Произошла ошибка sending_confirmation_message: {e}")

    async def sending_link_message(self, chat_id, username, meeting_appointed_time, meeting_link, meeting_duration, meeting_id):
        try:
            kyrgyzstan_timezone = pytz.timezone('Asia/Bishkek')
            current_time_kyrgyzstan = datetime.datetime.now(kyrgyzstan_timezone)
            meeting_time_kyrgyzstan = meeting_appointed_time - datetime.timedelta(hours=6)
            time_difference = meeting_time_kyrgyzstan - current_time_kyrgyzstan
            logging.info(f'Назначенное время встречи : {meeting_appointed_time}\nВстреча начнется через : {time_difference}')
            time_difference_minutes = (meeting_time_kyrgyzstan - current_time_kyrgyzstan).total_seconds() / 60

            if time_difference_minutes <= 1:
                logging.info(f"Время встречи наступило, {username}! Ссылка на встречу: {meeting_link}")
                await self.bot.send_message(chat_id=chat_id, text=f"Время встречи наступило, {username}! Ссылка на встречу: {meeting_link}")
                await self.db.create_pool()
                user_data = await self.user_db_manager.get_user(username)
                if user_data['user_type'] == 'professor':
                    self.message_handler.meeting_data[username] = {
                        'chat_id': chat_id,
                        'username': username,
                        'meeting_id': meeting_id,
                        'meeting_appointed_time': meeting_appointed_time,
                        'meeting_duration': meeting_duration
                    }
                elif user_data['user_type'] == 'student':
                    await self.stop_user_task(username)
                    logging.info(f'Задача для студента {username} остановлена.')

            elif 29 * 60 <= time_difference.total_seconds() <= 30 * 60:
                logging.info(f"Отправка напоминания на 30 минут... пользователю : {username}")
                await self.bot.send_message(chat_id=chat_id, text=f"Через 30 минут у вас будет встреча, {username}! Подготовьтесь.")
                logging.info("Дождаться времени встречи...")

        except Exception as e:
            logging.info(f"Произошла ошибка sending_message: {e}")

    async def main(self):
        try:
            await self.db.create_pool()
            if self.command_handler.active_users:
                logging.info(f'Активные пользователи main : {len(self.command_handler.active_users)}')
                for username in self.command_handler.active_users:
                    data = await self.user_db_manager.get_user(username)

                    if data['user_type'] == 'professor':
                        meetings = await self.professor_db_manager.get_meetings(data['id'])
                        meeting_data = await self.meeting_db_manager.sorting(meetings)
                        chat_id = await self.professor_db_manager.get_chat_id(data['username'])
                        if meeting_data is not None:
                            task = asyncio.create_task(self.sending_link_message(
                                chat_id, data['username'],
                                meeting_data['datetime'],
                                meeting_data['jitsiLink'],
                                meeting_data['duration'],
                                meeting_data['id'])

                            )
                            self.user_tasks[username] = task

                        else:
                            logging.info(f"У пользователя {data['username']} нет встреч")

                    elif data['user_type'] == 'student':
                        meetings = await self.student_db_manager.get_meetings(data['id'])
                        meeting_data = await self.meeting_db_manager.sorting(meetings)
                        chat_id = await self.student_db_manager.get_chat_id(data['username'])
                        if meeting_data is not None:
                            task = asyncio.create_task(self.sending_link_message(
                                chat_id, data['username'],
                                meeting_data['datetime'],
                                meeting_data['jitsiLink'],
                                meeting_data['duration'],
                                meeting_data['id'])
                            )
                            self.user_tasks[username] = task

                        else:
                            logging.info(f"У пользователя {data['username']} нет встреч")

                    if self.message_handler.meeting_data:
                        for username in self.message_handler.meeting_data:
                            professor_data = await self.professor_db_manager.get_data(username)
                            if professor_data:
                                meeting = self.message_handler.meeting_data[username]
                                self.message_handler.confirmation[meeting['chat_id']] = {
                                    'chat_id': meeting['chat_id'],
                                    'username': meeting['username'],
                                    'meeting_id': meeting['meeting_id'],

                                }

                                await self.sending_confirmation_message(
                                    professor_data['chat_id'],
                                    professor_data['username'],
                                    meeting['meeting_appointed_time'],
                                    meeting['meeting_duration'],
                                    meeting['meeting_id']
                                )

                            else:
                                logging.info(f'Пользователь {username} не является учителем, задача остановлена')

                    if self.meeting_not_marked:
                        for username, data in self.meeting_not_marked.items():
                            chat_id = data['chat_id']
                            meeting_id = data['meeting_id']
                            meeting_status = 'NOT MARKED'
                            await self.meeting_db_manager.update_status(meeting_id, meeting_status)
                            del self.message_handler.meeting_data[self.message_handler.confirmation[str(chat_id)]['username']]
                            del self.message_handler.confirmation[str(chat_id)]
                            logging.info(f'Время истекло. Встреча отмечена как NOT MARKED. статус: {meeting_status}')
                            await self.bot.send_message(chat_id, 'Вы не подтвердили встречу!\nвстреча останется не отмечанной', reply_markup=ReplyKeyboardRemove())
                            self.message_handler.user_data['current_state'] = 'idle'

                        self.meeting_not_marked.clear()

                await asyncio.gather(*self.user_tasks.values())

            else:
                logging.info('Нет активных пользователей')

        except Exception as e:
            logging.info(f"Произошла ошибка main: {e}")

    async def register_commands(self):
        await self.command_handler.register_commands()
        await self.message_handler.register_commands()


main_bot = MainBot()


async def run():
    await main_bot.main()


if __name__ == '__main__':
    logging.basicConfig(filename='bot_logs.log', level=logging.INFO, encoding='utf-8',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    loop = asyncio.get_event_loop()
    loop.create_task(main_bot.register_commands())
    aiocron.crontab('*/1 * * * *', func=lambda: asyncio.ensure_future(run()))
    executor.start_polling(main_bot.dp, skip_updates=True)
    loop.run_forever()
