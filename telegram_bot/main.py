# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import pytz
from datetime import datetime, timedelta
from .settings_bot import TOKEN
from .commands import start_command
from .database import get_user, sorted_meetings, get_meeting_professors, get_meeting_students, get_telegram_id

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


# Регистрируем обработчики команд
def username_callback(username):
    loop = asyncio.get_event_loop()
    loop.create_task(main(username))


dp.register_message_handler(lambda message: start_command(message, username_callback), commands=['start'])

# Функция, которая будет получать username и работать с ним


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


async def main(username):
    while True:
        if not username:
            print('username не найден!')
        else:
            user_data = get_user(username)
            if user_data['user_type'] == 'student':
                student_meetings = sorted_meetings(get_meeting_students(user_data['id']))
                chat_id = get_telegram_id(user_data['username'])
                await send_notification(chat_id, user_data['username'], student_meetings[0][1], student_meetings[0][2])

            elif user_data['user_type'] == 'professor':
                professor_meetings = sorted_meetings(get_meeting_professors(user_data['id']))
                chat_id = get_telegram_id(user_data['username'])
                await send_notification(chat_id, user_data['username'], professor_meetings[0][1], professor_meetings[0][2])

        await asyncio.sleep(60)  # Подождать 60 секунд перед следующей итерацией


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
