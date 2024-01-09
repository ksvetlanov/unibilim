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
import os
from dotenv import load_dotenv
from .settings_bot import DB_HOST, DB_PASSWORD, DB_USER, DB_NAME, LINK_TO_SCHEDULE
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
        self.bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
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
        self.new_meeting_tasks = {}
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

    async def stop_user_task(self, data, tasks):
        if data in tasks:
            task = tasks.pop(data)
            task.cancel()

    async def sending_new_meeting_message(self, payment_id, professor_id):
        try:
            professor_data = await self.professor_db_manager.get_professor_by_id(professor_id)
            if professor_data:
                await self.bot.send_message(chat_id=professor_data['chat_id'],
                                            text=f"{professor_data['username']}, у вас назначены новые встречи!\nДля получения подробной информации, перейдите по ссылке: {LINK_TO_SCHEDULE}")
                status = 'SENT'
                update_status_payments = await self.meeting_db_manager.update_status_payments(payment_id, status)
                if update_status_payments:
                    await self.stop_user_task(payment_id, self.new_meeting_tasks)
                    logging.info(f'sending_new_meeting_message обработан {professor_data["username"]}')
                else:
                    logging.info('Sending_new_meeting_message update_status_payments: payment status has not been updated')
            else:
                logging.info('sending_new_meeting_message get_professor_by_id: Professors details not received')

        except Exception as e:
            logging.info(f"Произошла ошибка sending_new_meeting_message: {e}")

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
                user_id = await self.meeting_db_manager.get_meeting_by_id(int(meeting_id))
                if user_id:
                    student_username = await self.student_db_manager.get_username(int(user_id['student_id']))
                    if student_username:
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
                        markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
                        await self.bot.send_message(chat_id, f"Прошла ли встреча с пользователем {student_username} ?\nДата и время встречи: {meeting_appointed_time.strftime('%Y-%m-%d %H:%M:%S')}", reply_markup=markup)
                        logging.info(f"Опрос отправлен пользователю {username}")
                    else:
                        logging.info('sending_confirmation_message get_username: student username not received')
                else:
                    logging.info('sending_confirmation_message get_meeting_by_id: Professor and student id not received')

                self.message_handler.user_data['username'] = username
                self.message_handler.user_data['chat_id'] = chat_id
                self.message_handler.user_data['meeting_id'] = meeting_id
                self.message_handler.user_data['current_state'] = 'waiting_confirmation'

            elif time_difference_minutes < 0:
                confirmation_id = await self.meeting_db_manager.get_meeting_confirmation_id(meeting_id)
                if confirmation_id:
                    current_confirmation_data = await self.meeting_db_manager.get_confirmation_data(confirmation_id)
                    if current_confirmation_data['confirmation_attempts'] != 3:
                        new_duration = current_confirmation_data['duration'] + datetime.timedelta(minutes=2)
                        new_confirmation_attempts = current_confirmation_data['confirmation_attempts'] + 1
                        update_meeting_confirmation = await self.meeting_db_manager.update_meeting_confirmation(confirmation_id, new_duration, new_confirmation_attempts)
                        if not update_meeting_confirmation:
                            logging.info('sending_confirmation_message update_meeting_confirmation: confirmation data has not been updated')

                    else:
                        await self.bot.send_message(chat_id,"Встреча не была подтверждена. Свяжитесь с администрацией.", reply_markup=ReplyKeyboardRemove())
                        logging.info(f'Пользователь {username} не подтвердил встречу, отправлено уведомление администрации')
                        self.message_handler.user_data['current_state'] = 'idle'
                        meeting_status = 'NOT MARKED'
                        confirmation_status = 'SENT'
                        await self.meeting_db_manager.update_status(meeting_id, meeting_status)
                        await self.meeting_db_manager.update_status_confirmation(confirmation_id, confirmation_status)
                        await self.message_handler.stop_user_task(meeting_id)
                else:
                    logging.info('sending_confirmation_message get_meeting_confirmation_id: id confirmation not received')

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
                if user_data:
                    if user_data['user_type'] == 'professor':
                        create_meetings_confirmation = await self.meeting_db_manager.create_meetings_confirmation(
                            chat_id, username, meeting_appointed_time, meeting_duration, status='DID NOT SENT',
                            meeting_id=meeting_id, professor_id=user_data['id'], confirmation_attempts=0
                        )
                        if not create_meetings_confirmation:
                            logging.info('sending_link_message create_meetings_confirmation: no confirmation record has been created in the database')

                        await self.stop_user_task(username, self.user_tasks)

                    elif user_data['user_type'] == 'student':
                        await self.stop_user_task(username, self.user_tasks)
                        logging.info(f'Задача для студента {username} остановлена.')
                else:
                    logging.info('sending_link_message get_user: user data not received')

            elif 29 * 60 <= time_difference.total_seconds() <= 30 * 60:
                current_user = await self.user_db_manager.get_user(username)
                if current_user['user_type'] == 'professor':
                    user_id = await self.meeting_db_manager.get_meeting_by_id(int(meeting_id))
                    student_username = await self.student_db_manager.get_username(int(user_id['student_id']))
                    logging.info(f"Отправка напоминания на 30 минут... пользователю : {username}")
                    await self.bot.send_message(chat_id=chat_id, text=f"Через 30 минут у вас будет встреча с пользователем {student_username}, {username}! Подготовьтесь.")
                    logging.info("Дождаться времени встречи...")

                elif current_user['user_type'] == 'student':
                    user_id = await self.meeting_db_manager.get_meeting_by_id(int(meeting_id))
                    professor_username = await self.professor_db_manager.get_professor_by_id(int(user_id['professor_id']))
                    logging.info(f"Отправка напоминания на 30 минут... пользователю : {username}")
                    await self.bot.send_message(chat_id=chat_id, text=f"Через 30 минут у вас будет встреча с пользователем {professor_username['username']}, {username}! Подготовьтесь.")
                    logging.info("Дождаться времени встречи...")

        except Exception as e:
            logging.info(f"Произошла ошибка sending_link_message: {e}")

    async def processing_new_meetings(self):
        try:
            new_meeting_data = await self.meeting_db_manager.get_new_meeting()
            if new_meeting_data:
                for new_meeting in new_meeting_data:
                    task = asyncio.create_task(self.sending_new_meeting_message(
                        new_meeting['id'],
                        new_meeting['professor_id']
                    ))
                    self.new_meeting_tasks[new_meeting['id']] = task
                await asyncio.gather(*self.new_meeting_tasks.values())

        except Exception as e:
            logging.info(f"Произошла ошибка processing_new_meetings: {e}")

    async def link_processing(self):
        try:
            if self.command_handler.active_users:
                for username in self.command_handler.active_users:
                    data = await self.user_db_manager.get_user(username)

                    if data['user_type'] == 'professor':
                        meetings = await self.professor_db_manager.get_meetings(data['id'])
                        if meetings:
                            meeting_data = await self.meeting_db_manager.sorting(meetings)
                            chat_id = await self.professor_db_manager.get_chat_id(data['username'])
                            if chat_id:
                                if meeting_data is not None:
                                    task = asyncio.create_task(self.sending_link_message(
                                        chat_id,
                                        data['username'],
                                        meeting_data['datetime'],
                                        meeting_data['jitsiLink'],
                                        meeting_data['duration'],
                                        meeting_data['id'])
                                    )
                                    self.user_tasks[username] = task

                                else:
                                    logging.info(f"У пользователя {data['username']} нет встреч")
                            else:
                                logging.info(f'link_processing get_chat_id: the chat_id of the {data["username"]} user was not received')
                        else:
                            logging.info(f'link_processing get_meetings: meetings of the {data["username"]} user have been received')

                    elif data['user_type'] == 'student':
                        meetings = await self.student_db_manager.get_meetings(data['id'])
                        if meetings:
                            meeting_data = await self.meeting_db_manager.sorting(meetings)
                            chat_id = await self.student_db_manager.get_chat_id(data['username'])
                            if chat_id:
                                if meeting_data is not None:
                                    task = asyncio.create_task(self.sending_link_message(
                                        chat_id,
                                        data['username'],
                                        meeting_data['datetime'],
                                        meeting_data['jitsiLink'],
                                        meeting_data['duration'],
                                        meeting_data['id'])
                                    )
                                    self.user_tasks[username] = task

                                else:
                                    logging.info(f"У пользователя {data['username']} нет встреч")
                            else:
                                logging.info(f'link_processing get_chat_id: the chat_id of the {data["username"]} user was not received')
                        else:
                            logging.info(f'link_processing get_meetings: meetings of the {data["username"]} user have been received')

                await asyncio.gather(*self.user_tasks.values())

            else:
                logging.info('Нет активных пользователей')

        except Exception as e:
            logging.info(f"Произошла ошибка link_processing: {e}")

    async def confirmation_processing(self):
        try:
            confirmation_data = await self.meeting_db_manager.get_unsent_meetings_confirmation()
            if confirmation_data:
                logging.info('обработка подтверждений')
                for confirmation in confirmation_data:
                    task = asyncio.create_task(self.sending_confirmation_message(
                        confirmation['chat_id'],
                        confirmation['username'],
                        confirmation['appointed_time'],
                        confirmation['duration'],
                        confirmation['meeting_id']
                    ))
                    self.message_handler.confirmation_tasks[confirmation['meeting_id']] = task
                await asyncio.gather(*self.message_handler.confirmation_tasks.values())

        except Exception as e:
            logging.info(f"Произошла ошибка confirmation_processing: {e}")

    async def main(self):
        try:
            await self.db.create_pool()
            if self.command_handler.active_users:
                logging.info(f'Активные пользователи : {len(self.command_handler.active_users)}')
                await asyncio.gather(self.link_processing(),
                                     self.confirmation_processing(),
                                     self.processing_new_meetings()
                                     )
            else:
                logging.info('Нет активных пользователей')

        except Exception as e:
            logging.info(f"Произошла ошибка main: {e}")

    async def register_commands(self):
        await self.command_handler.register_commands()
        await self.message_handler.register_commands()


load_dotenv()
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
