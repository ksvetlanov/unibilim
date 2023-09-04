import asyncio
import logging
import datetime
import aiocron
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from .settings_bot import TOKEN
from .commands import start_command, active_users
from .database import sort_meetings, get_meeting_students, get_meeting_professors, get_user, get_telegram_id
import pytz


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


dp.register_message_handler(start_command, commands=['start'])

link_sent = {}


async def send_question(chat_id, meeting_id):
    pass


async def sending_message(chat_id, username, meeting_appointed_time, meeting_link, meeting_duration, meeting_id):

    # текущее время кыргызстана
    kyrgyzstan_timezone = pytz.timezone('Asia/Bishkek')
    current_time_kyrgyzstan = datetime.datetime.now(kyrgyzstan_timezone)

    # приобразование назначенного времени встречи в время для кыргызстана
    meeting_time_kyrgyzstan = meeting_appointed_time - datetime.timedelta(hours=6)

    time_difference = meeting_time_kyrgyzstan - current_time_kyrgyzstan
    print(f'Назначенное время встречи : {meeting_time_kyrgyzstan}\nВстреча начнется через : {time_difference}')

    time_difference_minutes = (meeting_time_kyrgyzstan - current_time_kyrgyzstan).total_seconds() / 60

    if time_difference_minutes <= 1:
        print(f"Время встречи наступило, {username}! Ссылка на встречу: {meeting_link}")
        await bot.send_message(chat_id=chat_id,
                               text=f"Время встречи наступило, {username}! Ссылка на встречу: {meeting_link}")

    elif 29 * 60 <= time_difference.total_seconds() <= 30 * 60:
        print(f"Отправка напоминания на 30 минут... пользователю : {username}")
        await bot.send_message(chat_id=chat_id,
                               text=f"Через 30 минут у вас будет встреча, {username}! Подготовьтесь.")
        print("Дождаться времени встречи...")


async def main():
    if active_users:
        print(f'Активные пользователи main : {active_users}')
        for username in active_users:
            user_data = get_user(username)
            if user_data['user_type'] == 'student':
                student_meetings = sort_meetings(get_meeting_students(user_data['id']))
                chat_id = get_telegram_id(user_data['username'])
                if student_meetings is not None:
                    print(f'Обработка в main пользователя : {user_data["username"]}')
                    await sending_message(chat_id, user_data['username'], student_meetings[1], student_meetings[2], student_meetings[6], student_meetings[0])

                else:
                    print('нет встреч')

            elif user_data['user_type'] == 'professor':
                professor_meetings = sort_meetings(get_meeting_professors(user_data['id']))
                chat_id = get_telegram_id(user_data['username'])
                if professor_meetings is not None:
                    print(f'Обработка в main пользователя : {user_data["username"]}')
                    await sending_message(chat_id, user_data['username'], professor_meetings[1], professor_meetings[2], professor_meetings[6], professor_meetings[0])

                else:
                    print('нет встреч')

    else:
        print('Нет активных пользователей')


if __name__ == '__main__':
    aiocron.crontab('* * * * *', func=main)
    executor.start_polling(dp, skip_updates=True)
