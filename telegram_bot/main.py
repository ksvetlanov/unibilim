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
from collections import defaultdict


# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Регистрируем обработчики команд
dp.register_message_handler(start_command, commands=['start'])

# В функции send_notification измените часть с ожиданием
notifications_sent = defaultdict(bool)
last_notification_time = {}


async def send_notification(chat_id, username, meeting_time, meeting_link):
    print("Отправка уведомления...")
    current_time = datetime.now(pytz.utc)  # Получаем текущее время с учетом UTC

    # Коррекция времени встречи на 6 часов назад
    corrected_meeting_time = meeting_time - timedelta(hours=6)

    time_until_meeting = corrected_meeting_time - current_time
    print("Время до встречи:", time_until_meeting, corrected_meeting_time)

    if time_until_meeting > timedelta(seconds=0):
        last_notification = last_notification_time.get(corrected_meeting_time, None)
        if last_notification is None or (current_time - last_notification).total_seconds() >= 60 * 30:
            if timedelta(minutes=30) <= time_until_meeting <= timedelta(minutes=30, seconds=59):
                print("Отправка напоминания на 30 минут...")
                await bot.send_message(chat_id=chat_id,
                                       text=f"Через 30 минут у вас будет встреча, {username}! Подготовьтесь.")

            print("Дождаться времени встречи...")
            event = asyncio.Event()
            await asyncio.sleep(time_until_meeting.total_seconds())
            event.set()

            # Проверяем, что это первое уведомление для данной встречи
            if last_notification_time.get(meeting_time) != current_time:
                # Отправка ссылки на встречу
                await bot.send_message(chat_id=chat_id,
                                       text=f"Время встречи наступило, {username}! Ссылка на встречу: {meeting_link}")
                print("Ссылка на встречу отправлена.")
                last_notification_time[meeting_time] = current_time
    else:
        print("Время встречи уже прошло. Нет необходимости отправлять уведомление.")


schedule_lock = asyncio.Lock()


async def schedule_check_and_send():
    async with schedule_lock:
        current_username = get_current_username()
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