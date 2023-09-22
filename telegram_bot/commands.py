import psycopg2
from aiogram import types
from .settings_bot import LINK_TO_WEBSITE
from .database import get_user, update_student_data, update_professor_data


active_users = {}


def add_user_to_active(username, user_id):
    active_users[username] = user_id


def remove_user_from_active(username):
    if username in active_users:
        del active_users[username]


async def start_command(message: types.Message):

    try:
        user = message.from_user
        chat_username = message.chat.username

        user_data = get_user(chat_username)
        if user_data:
            if user_data['user_type'] == 'student':
                update_student_data(user_data['username'], user.id)
                await message.reply(f"Привет {user_data['username']}")
                add_user_to_active(user_data['username'], user.id)
                print(f'Активные пользователи : {active_users}')
            elif user_data['user_type'] == 'professor':
                update_professor_data(user_data['username'], user.id)
                await message.reply(f"Привет, {user_data['username']}! Я буду напоминать вам о предстоящих встречах и присылать ссылки в назначенное время, где будут проводиться занятия.")
                add_user_to_active(user_data['username'], user.id)
                print(f'Активные пользователи start : {active_users}')
        else:
            await message.reply(f"Пользователь не найден в базе данных. Посетите этот сайт: {LINK_TO_WEBSITE}")

    except psycopg2.Error as db_error:
        print(f"Произошла ошибка при обращении к базе данных: {db_error}")
    except Exception as e:
        print(f"Произошла неизвестная ошибка: {e}")