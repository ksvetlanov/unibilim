import asyncio
import logging
import aiocron
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import pytz
from datetime import datetime, timedelta
from .settings_bot import TOKEN
from .commands import start_command, get_current_username
from .database import get_user, sorted_meetings, get_meeting_professors, get_meeting_students, get_telegram_id

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


# Регистрируем обработчики команд


dp.register_message_handler(start_command, commands=['start'])


async def send_notification(chat_id, username, meeting_time, meeting_link):
    print("Sending notification...")
    current_time = datetime.now(pytz.utc)  # Получаем текущее время с учетом UTC

    time_until_meeting = meeting_time - current_time
    print("Time until meeting:", time_until_meeting, meeting_time)

    if timedelta(minutes=30) <= time_until_meeting <= timedelta(minutes=30, seconds=59):
        print("Sending 30 minutes reminder...")
        await bot.send_message(chat_id=chat_id, text=f"Через 30 минут у вас будет встреча, {username}! Подготовьтесь.")

    if time_until_meeting <= timedelta(seconds=0):
        print("Waiting until meeting time...")
        await asyncio.sleep(-time_until_meeting.total_seconds())  # Ожидание до начала встречи

        # Отправка ссылки на встречу
        await bot.send_message(chat_id=chat_id,
                               text=f"Время встречи наступило, {username}! Ссылка на встречу: {meeting_link}")
        print("Meeting link sent.")


async def schedule_check_and_send():
    current_username = get_current_username()
    print(current_username, 'main')# Получаем текущее значение username
    if current_username:
        user_data = get_user(current_username)
        if user_data['user_type'] == 'student':
            student_meetings = sorted_meetings(get_meeting_students(user_data['id']))
            chat_id = get_telegram_id(user_data['username'])
            await send_notification(chat_id, user_data['username'], student_meetings[0][1], student_meetings[0][2])
        elif user_data['user_type'] == 'professor':
            professor_meetings = sorted_meetings(get_meeting_professors(user_data['id']))
            chat_id = get_telegram_id(user_data['username'])
            await send_notification(chat_id, user_data['username'], professor_meetings[0][1], professor_meetings[0][2])


# Запуск бота
if __name__ == '__main__':
    # Регистрация планировщика задач
    aiocron.crontab('* * * * *', func=schedule_check_and_send)

    # Запуск бота
    executor.start_polling(dp, skip_updates=True)