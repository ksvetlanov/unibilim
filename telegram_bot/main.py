import datetime
import asyncio
import logging
import aiocron
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import StatesGroup, State
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

    async def sending_confirmation_message(self, chat_id, username, meeting_appointed_time, meeting_duration):
        try:
            kyrgyzstan_timezone = pytz.timezone('Asia/Bishkek')
            current_time_kyrgyzstan = datetime.datetime.now(kyrgyzstan_timezone)
            meeting_time_kyrgyzstan = meeting_appointed_time - datetime.timedelta(hours=6)
            meeting_end_time = meeting_time_kyrgyzstan + meeting_duration
            log_meeting_time = meeting_end_time + datetime.timedelta(hours=6)
            time_difference = meeting_end_time - current_time_kyrgyzstan
            print(f'Встреча закончится в : {log_meeting_time}\nОпрос придет пользователю {username} через : {time_difference}')
            time_difference_minutes = (meeting_end_time - current_time_kyrgyzstan).total_seconds() / 60

            if 0 < time_difference_minutes <= 1:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
                markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))

                await self.bot.send_message(chat_id, "Прошла ли встреча?", reply_markup=markup)
                print(f"Опрос отправлен пользователю {username}")

                self.message_handler.user_data['current_state'] = 'waiting_confirmation'

        except Exception as e:
            print(f"Произошла ошибка sending_confirmation_message: {e}")

    async def sending_link_message(self, chat_id, username, meeting_appointed_time, meeting_link, meeting_duration, meeting_id):
        try:
            kyrgyzstan_timezone = pytz.timezone('Asia/Bishkek')
            current_time_kyrgyzstan = datetime.datetime.now(kyrgyzstan_timezone)
            meeting_time_kyrgyzstan = meeting_appointed_time - datetime.timedelta(hours=6)
            time_difference = meeting_time_kyrgyzstan - current_time_kyrgyzstan
            print(f'Назначенное время встречи : {meeting_appointed_time}\nВстреча начнется через : {time_difference}')
            time_difference_minutes = (meeting_time_kyrgyzstan - current_time_kyrgyzstan).total_seconds() / 60

            if time_difference_minutes <= 1:
                print(f"Время встречи наступило, {username}! Ссылка на встречу: {meeting_link}")
                await self.bot.send_message(chat_id=chat_id, text=f"Время встречи наступило, {username}! Ссылка на встречу: {meeting_link}")

                self.message_handler.meeting_data[username] = {
                    'chat_id': chat_id,
                    'username': username,
                    'meeting_id': meeting_id,
                    'meeting_appointed_time': meeting_appointed_time,
                    'meeting_duration': meeting_duration
                    }

            elif 29 * 60 <= time_difference.total_seconds() <= 30 * 60:
                print(f"Отправка напоминания на 30 минут... пользователю : {username}")
                await self.bot.send_message(chat_id=chat_id, text=f"Через 30 минут у вас будет встреча, {username}! Подготовьтесь.")
                print("Дождаться времени встречи...")

        except Exception as e:
            print(f"Произошла ошибка sending_message: {e}")

    async def main(self):
        tasks = []
        try:
            await self.db.create_pool()
            if self.command_handler.active_users:
                print(f'Активные пользователи main : {len(self.command_handler.active_users)}')
                for username in self.command_handler.active_users:
                    data = await self.user_db_manager.get_user(username)

                    if data['user_type'] == 'professor':
                        meetings = await self.professor_db_manager.get_meetings(data['id'])
                        meeting_data = await self.meeting_db_manager.sorting(meetings)
                        chat_id = await self.professor_db_manager.get_chat_id(data['username'])
                        if meeting_data is not None:
                            tasks.append(self.sending_link_message(
                                chat_id, data['username'],
                                meeting_data['datetime'],
                                meeting_data['jitsiLink'],
                                meeting_data['duration'],
                                meeting_data['id'])
                            )

                        else:
                            print(f"У пользователя {data['username']} нет встреч")

                    elif data['user_type'] == 'student':
                        meetings = await self.student_db_manager.get_meetings(data['id'])
                        meeting_data = await self.meeting_db_manager.sorting(meetings)
                        chat_id = await self.student_db_manager.get_chat_id(data['username'])
                        if meeting_data is not None:
                            tasks.append(self.sending_link_message(
                                chat_id, data['username'],
                                meeting_data['datetime'],
                                meeting_data['jitsiLink'],
                                meeting_data['duration'],
                                meeting_data['id'])
                            )

                        else:
                            print(f"У пользователя {data['username']} нет встреч")

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
                                )

                            else:
                                print('текущий пользователь не учитель')

                await asyncio.gather(*tasks)

            else:
                print('Нет активных пользователей')

        except Exception as e:
            print(f"Произошла ошибка main: {e}")

    async def register_commands(self):
        await self.command_handler.register_commands()
        await self.message_handler.register_commands()


main_bot = MainBot()


async def run():
    await main_bot.main()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(main_bot.register_commands())
    aiocron.crontab('*/1 * * * *', func=lambda: asyncio.ensure_future(run()))
    executor.start_polling(main_bot.dp, skip_updates=True)
    loop.run_forever()
