# commands.py
import psycopg2
from aiogram import types
from .database import get_user, update_student_data, update_professor_data, get_meeting_professors, sorted_meetings, get_telegram_id
from .settings_bot import LINK_TO_WEBSITE


current_username = None


def update_current_username(username):
    global current_username
    current_username = username


async def start_command(message: types.Message):
    try:
        user = message.from_user
        chat_username = message.chat.username

        user_data = get_user(chat_username)
        if user_data:
            if user_data['user_type'] == 'student':
                update_student_data(user_data['username'], user.id)
                await message.reply(f"Привет {user_data['username']}")
                update_current_username(user_data['username'])

            elif user_data['user_type'] == 'professor':
                update_professor_data(user_data['username'], user.id)
                await message.reply(f"Привет {user_data['username']}")
                update_current_username(user_data['username'])

        else:
            await message.reply(f"Пользователь не найден в базе данных. Посетите этот сайт: {LINK_TO_WEBSITE}")

    except psycopg2.Error as db_error:
        await message.reply(f"Произошла ошибка при обращении к базе данных: {db_error}")
    except Exception as e:
        await message.reply(f"Произошла неизвестная ошибка: {e}")


def get_current_username():
    return current_username
