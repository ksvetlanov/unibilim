import asyncio
import os
import shutil
import subprocess
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from .settings_bot import DB_PASSWORD, PASSWORD_COPY_FILE, PASSWORD_NAME_FILE_LIST, DB_USER, DB_NAME


class MessageServices:
    async def list_files_in_directory(self, directory):
        file_list = []
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_list.append(os.path.join(root, file))
            return file_list

        except Exception as e:
            print(f"Произошла ошибка list_files_in_directory: {e}")

    async def is_git_file(self, file_path):
        return file_path.startswith('.\\.git\\')


class MessageHandler:
    def __init__(self, bot, dp, database, user_db_manager, professor_db_manager, student_db_manager, meeting_db_manager, command_handler, my_state):
        self.bot = bot
        self.dp = dp
        self.db = database
        self.user_db_manager = user_db_manager
        self.professor_db_manager = professor_db_manager
        self.student_db_manager = student_db_manager
        self.meeting_db_manager = meeting_db_manager
        self.message_services = MessageServices()
        self.command_handler = command_handler
        self.my_state = my_state
        self.confirmation = {}
        self.meeting_data = {}
        self.user_data = {}

    async def handle_confirmation_response(self, message: types.Message, user_data):
        try:

            chat_id = message.chat.id
            if str(chat_id) in self.confirmation:
                response = message.text.lower()

                if response == 'да':
                    await message.reply("Встреча прошла успешно!", reply_markup=ReplyKeyboardRemove())
                    meeting_status = 'ACCEPTED'
                    await self.meeting_db_manager.update_status(self.confirmation[str(chat_id)]['meeting_id'], meeting_status)
                    del self.meeting_data[self.confirmation[str(chat_id)]['username']]
                    del self.confirmation[str(chat_id)]
                    print(f'Встреча успешно состоялась. статус: {meeting_status}')
                    user_data['current_state'] = 'idle'

                elif response == 'нет':
                    await message.reply("Встреча не состоялась.", reply_markup=ReplyKeyboardRemove())
                    meeting_status = 'DECLINED'
                    await self.meeting_db_manager.update_status(self.confirmation[str(chat_id)]['meeting_id'], meeting_status)
                    del self.meeting_data[self.confirmation[str(chat_id)]['username']]
                    del self.confirmation[str(chat_id)]
                    print(f'Встреча не состоялась. статус: {meeting_status}')
                    user_data['current_state'] = 'idle'

                else:
                    await message.reply("неизвестный ответ")
            else:
                print('handle_confirmation_response: chat_id нет в confirmation')

        except Exception as e:
            print(f"Произошла ошибка handle_confirmation_response: {e}")

    async def backup_password_message(self, message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        print(f"Текущее состояние: {current_state}")
        password = message.text
        try:
            if password == f'{DB_PASSWORD}':
                pg_dump_path = "\"C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe\""
                os.environ['PGPASSWORD'] = password
                backup_commandd = "{} -U {} -d {} -f backup.sql".format(pg_dump_path, f'{DB_USER}', f'{DB_NAME}')
                process = subprocess.Popen(backup_commandd, shell=True)
                process.wait()
                if process.returncode == 0:

                    with open('backup.sql', 'rb') as backup_file:
                        await message.reply_document(backup_file, caption="Бэкап успешно выполнен и файл отправлен.")
                        os.remove('backup.sql')
                        await state.finish()
                else:
                    await message.reply("Произошла ошибка при создании бэкапа. Пожалуйста, проверьте введенные данные и попробуйте еще раз.")
            else:
                await message.reply("Неверный пароль. Попробуйте еще раз.")

        except FileNotFoundError as e:
            print(f"Произошла ошибка: {e}. Убедитесь, что у вас установлен PostgreSQL и правильно указан путь к утилите pg_dump.")
        except Exception as e:
            print(f"Произошла неизвестная ошибка: {e}")

    async def check_file_name_message(self, message: types.Message, state: FSMContext):
        try:
            project_directory = '.'
            destination_directory = './telegram_bot/garbage'
            files_in_project = await self.message_services.list_files_in_directory(project_directory)
            filtered_file_list = [file for file in files_in_project if not await self.message_services.is_git_file(file)]
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

        except Exception as e:
            print(f"Произошла ошибка check_file_name_message: {e}")

    async def copy_file_password_message(self, message: types.Message, state: FSMContext):
        try:
            password = message.text
            if password == PASSWORD_COPY_FILE:
                await message.answer("Пароль верен. Теперь введите название файла:")
                await state.finish()
                await self.my_state.check_file_name.set()

            else:
                await message.answer(f"Неверный пароль. Попробуйте снова.")

        except Exception as e:
            print(f"Произошла ошибка copy_file_password_message: {e}")

    async def file_name_list_message(self, message: types.Message, state: FSMContext):
        try:
            if message.text == PASSWORD_NAME_FILE_LIST:
                project_directory = '.'
                files_in_project = await self.message_services.list_files_in_directory(project_directory)
                filtered_file_list = [file for file in files_in_project if not await self.message_services.is_git_file(file)]

                for i in filtered_file_list:
                    await message.reply(f"{i}")
                    await asyncio.sleep(1)

                await message.reply(f"Это весь список файлов которые на сервере.")
                await state.finish()

            else:
                await message.answer(f"Неверный пароль. Попробуйте снова.")

        except Exception as e:
            print(f"Произошла ошибка file_name_list_message: {e}")

    async def password_reset(self, message: types.Message, state: FSMContext):
        await self.db.create_pool()
        try:
            url = 'http://127.0.0.1:8000/accounts/password-reset/'
            chat_username = message.chat.username
            new_password = message.text
            if len(new_password) >= 8:
                user_data = await self.user_db_manager.get_user(chat_username)
                data = {"user_id": f'{user_data["user__id"]}', "new_password": f"{new_password}"}
                response = requests.post(url, data=data)
                await message.answer(f"{response.status_code} : {response.json()}")
                await state.finish()

            else:
                await message.answer("такой пароль не подходит")

        except Exception as e:
            print(f"Произошла ошибка file_name_list_message: {e}")

    async def password_reset_code(self, message: types.Message, state: FSMContext):
        chat_id = message.chat.id
        user_code = message.text
        try:
            correct_code = self.command_handler.codes.get(chat_id)
            if user_code == correct_code:
                await message.answer(f"Верный код! Доступ разрешен\nПридумайте новый пароль !")
                del self.command_handler.codes[chat_id]
                await state.finish()
                await self.my_state.password_reset.set()

            else:
                await message.answer("Неверный код. Попробуйте еще раз.")

        except Exception as e:
            print(f"Произошла ошибка password_reset_code: {e}")

    async def register_commands(self):
        self.dp.register_message_handler(
            lambda message: self.handle_confirmation_response(message, self.user_data),
            lambda message: self.user_data.get('current_state') == 'waiting_confirmation',
        )
        self.dp.register_message_handler(self.backup_password_message, state=self.my_state.backup_password)
        self.dp.register_message_handler(self.copy_file_password_message, state=self.my_state.copy_file_password)
        self.dp.register_message_handler(self.check_file_name_message, state=self.my_state.check_file_name)
        self.dp.register_message_handler(self.file_name_list_message, state=self.my_state.file_name_list_password)
        self.dp.register_message_handler(self.password_reset, state=self.my_state.password_reset)
        self.dp.register_message_handler(self.password_reset_code, state=self.my_state.password_reset_code)


