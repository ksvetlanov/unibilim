import psycopg2
from aiogram import types
from .database import get_user, update_student_data, update_professor_data


async def start_command(message: types.Message):
    try:
        user = message.from_user
        chat_username = message.chat.username

        user_data = get_user(chat_username)
        if user_data['user_type'] == 'student':
            update_student_data(user_data['username'], user.id)
            await message.reply(
                f"Данные пользователя чата обновлены. Новый telegram_id: {user_data['surname']}\n"
            )

        elif user_data['user_type'] == 'professor':
            update_professor_data(user_data['username'], user.id)
            await message.reply(
                f"Данные пользователя чата обновлены. Новый telegram_id: {user_data['surname']}\n"
            )

        else:
            await message.reply("Пользователь не найден в базе данных.")

    except psycopg2.Error as db_error:
        await message.reply(f"Произошла ошибка при обращении к базе данных: {db_error}")
    except Exception as e:
        await message.reply(f"Произошла неизвестная ошибка: {e}")
