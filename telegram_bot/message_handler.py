import asyncio
import subprocess
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
import os
import shutil
from .database import update_meeting_status
from .settings_bot import DB_PASSWORD, DB_USER, DB_NAME, PASSWORD_COPY_FILE, PASSWORD_NAME_FILE_LIST
from .command_handler import MyState

confirmation_professors = {}
meeting_info = {}


def list_files_in_directory(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def is_git_file(file_path):
    return file_path.startswith('.\\.git\\')


def professors_meeting_data(username, chat_id, meeting_id, ):
    confirmation_professors[chat_id] = {'chat_id': chat_id, 'username': username, 'meeting_id': meeting_id}


def remove_meeting_info(username):
    global meeting_info
    if username in meeting_info:
        del meeting_info[username]


def add_meeting_main(chat_id, username, meeting_id, meeting_duration):
    meeting_info[username] = {'chat_id': chat_id, 'username': username, 'meeting_id': meeting_id,
                              'meeting_duration': meeting_duration}


async def handle_user_response(message: types.Message):
    user_id = str(message.from_user.id)
    response = message.text.lower()

    try:
        if user_id in confirmation_professors:
            professor_data = confirmation_professors[user_id]
            meeting_id = professor_data['meeting_id']
            username = professor_data['username']

            if response == 'да':
                await message.answer("Встреча прошла успешно!", reply_markup=ReplyKeyboardRemove())
                meeting_status = 'ACCEPTED'
                print(f'Встреча не состоялась. статус : {meeting_status}')
                update_meeting_status(meeting_id, meeting_status)
                remove_meeting_info(username)

            elif response == 'нет':
                await message.answer("Встреча не состоялась.", reply_markup=ReplyKeyboardRemove())
                meeting_status = 'DECLINED'
                print(f'Встреча не состоялась. статус : {meeting_status}')
                update_meeting_status(meeting_id, meeting_status)
                remove_meeting_info(username)
        else:
            await message.answer("Извините, что-то пошло не так. Попробуйте позже.", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


async def check_password_db(message: types.Message, state: FSMContext):
    password = message.text
    if password == f'{DB_PASSWORD}':
        pg_dump_path = "\"C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe\""  # Укажите полный путь к pg_dump

        # Установите переменную окружения PGPASSWORD
        os.environ['PGPASSWORD'] = password

        # Выполните команду бэкапа
        backup_commandd = "{} -U {} -d {} -f backup.sql".format(pg_dump_path, f'{DB_USER}', f'{DB_NAME}')
        process = subprocess.Popen(backup_commandd, shell=True)
        process.wait()

        # Проверьте, была ли команда успешно выполнена
        if process.returncode == 0:
            # Отправьте файл пользователю
            with open('backup.sql', 'rb') as backup_file:
                await message.reply_document(backup_file, caption="Бэкап успешно выполнен и файл отправлен.")
                await state.finish()
        else:
            await message.reply(
                "Произошла ошибка при создании бэкапа. Пожалуйста, проверьте введенные данные и попробуйте еще раз.")
    else:
        await message.reply("Неверный пароль. Попробуйте еще раз.")


async def check_name_file(message: types.Message, state: FSMContext):
    project_directory = '.'
    destination_directory = './telegram_bot/garbage'
    files_in_project = list_files_in_directory(project_directory)
    filtered_file_list = [file for file in files_in_project if not is_git_file(file)]
    file_name = message.text
    if file_name in filtered_file_list:
        shutil.copy(file_name, destination_directory)
        file_name = os.path.basename(file_name)
        copied_file_path = os.path.join(destination_directory, file_name)
        with open(copied_file_path, 'rb') as file:
            await message.reply_document(file, caption="Файл скопирован и отправлен.")
            os.remove(copied_file_path)
        await state.finish()

    else:
        await message.reply(f"Такого файла нет на сервере!")


async def check_password_copy_file(message: types.Message, state: FSMContext):
    if message.text == PASSWORD_COPY_FILE:
        await message.answer("Пароль верен. Теперь введите название файла:")
        await state.finish()
        await MyState.check_name_file_state.set()
    else:
        await message.answer(f"Неверный пароль. Попробуйте снова.")


async def check_password_list_file_name(message: types.Message, state: FSMContext):
    if message.text == PASSWORD_NAME_FILE_LIST:
        project_directory = '.'
        files_in_project = list_files_in_directory(project_directory)
        filtered_file_list = [file for file in files_in_project if not is_git_file(file)]

        for i in filtered_file_list:
            await message.reply(f"{i}")
            await asyncio.sleep(1)

        await message.reply(f"Это весь список файлов которые на сервере.")
        await state.finish()

    else:
        await message.answer(f"Неверный пароль. Попробуйте снова.")
