import asyncio
import logging
import datetime
import aiocron
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
import pytz
from .settings_bot import TOKEN
from .command_handler import start_command, active_users, backup_command, get_copy_file_command, MyState, get_file_name_command
from .database import sort_meetings, get_meeting_students, get_meeting_professors, get_user, get_telegram_id, get_professor_data
from .message_handler import meeting_info, add_meeting_main, professors_meeting_data, remove_meeting_info, handle_user_response, check_password_db, check_password_copy_file, check_name_file, check_password_list_file_name


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


dp.register_message_handler(start_command, commands=['start'])
dp.register_message_handler(backup_command, commands=['backup'])
dp.register_message_handler(get_copy_file_command, commands=['get_file'])
dp.register_message_handler(get_file_name_command, commands=['get_file_name'])
dp.register_message_handler(handle_user_response, Text(equals=['да', 'нет'], ignore_case=True))
dp.register_message_handler(check_password_db, state=MyState.check_password_db_state)
dp.register_message_handler(check_password_copy_file, state=MyState.check_password_copy_file_state)
dp.register_message_handler(check_name_file, state=MyState.check_name_file_state)
dp.register_message_handler(check_password_list_file_name, state=MyState.check_password_list_file_name_state)
initial_time = datetime.datetime.strptime("01:00:00", "%H:%M:%S")
user_states_copy_file = {}


def subtract_one_minute():
    global initial_time
    initial_time -= datetime.timedelta(minutes=1)
    return initial_time


def reverse_time():
    global initial_time
    initial_time = initial_time.replace(hour=1, minute=0, second=0)
    return initial_time


async def send_question(user_id):
    print('Обработка send_question')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))

    await bot.send_message(
        user_id,
        "Прошла ли встреча?",
        reply_markup=markup,
    )


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
        add_meeting_main(chat_id, username, meeting_id, meeting_duration)

    elif 29 * 60 <= time_difference.total_seconds() <= 30 * 60:
        print(f"Отправка напоминания на 30 минут... пользователю : {username}")
        await bot.send_message(chat_id=chat_id,
                               text=f"Через 30 минут у вас будет встреча, {username}! Подготовьтесь.")
        print("Дождаться времени встречи...")


async def main():
    if active_users:
        print(f'Активные пользователи main : {active_users}')
        tasks = []
        for username in active_users:
            user_data = get_user(username)
            if user_data['user_type'] == 'student':
                student_meetings = sort_meetings(get_meeting_students(user_data['id']))
                chat_id = get_telegram_id(user_data['username'])
                if student_meetings is not None:
                    print(f'Обработка в main пользователя : {user_data["username"]}')
                    tasks.append(sending_message(chat_id, user_data['username'], student_meetings[1], student_meetings[2], student_meetings[6], student_meetings[0]))
                else:
                    print(f"У пользователя {user_data['username']} нет встреч")

            elif user_data['user_type'] == 'professor':
                professor_meetings = sort_meetings(get_meeting_professors(user_data['id']))
                chat_id = get_telegram_id(user_data['username'])
                if professor_meetings is not None:
                    print(f'Обработка в main пользователя : {user_data["username"]}')
                    tasks.append(sending_message(chat_id, user_data['username'], professor_meetings[1], professor_meetings[2], professor_meetings[6], professor_meetings[0]))
                else:
                    print(f"У пользователя {user_data['username']} нет встреч")

            if meeting_info:
                print('Обработка send_question')
                timer = subtract_one_minute()
                print(f'Опрос придет пользователю {username} через : {timer.strftime("%H:%M:%S")}')
                if username in meeting_info:  # Используйте переменную username для поиска в словаре
                    meeting_info_data = meeting_info[username]  # Получаем данные из словаря по username
                    meeting_id = meeting_info_data['meeting_id']
                    chat_id = meeting_info_data['chat_id']
                    meeting_duration = meeting_info_data['meeting_duration']
                    professor_data = get_professor_data(username)
                    if professor_data:
                        if professor_data['user_type'] == 'professor':
                            professors_meeting_data(username, chat_id, meeting_id)
                            await asyncio.sleep(meeting_duration.total_seconds())
                            reverse_time()
                            await send_question(professor_data['chat_id'])
                            remove_meeting_info(username)

                        else:
                            print('текущий пользователь не professor')
                    else:
                        print('None professor_data')
                else:
                    print(f'Нет данных для пользователя {username} в meeting_info')

        await asyncio.gather(*tasks)
    else:
        print('Нет активных пользователей')


if __name__ == '__main__':
    aiocron.crontab('* * * * *', func=main)
    executor.start_polling(dp, skip_updates=True)




