import asyncio
import logging
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
                    file_path = os.path.join(root, file)
                    normalized_path = os.path.normpath(file_path)
                    file_list.append(normalized_path)
            return file_list

        except Exception as e:
            logging.info(f"Произошла ошибка list_files_in_directory: {e}")

    async def is_git_file(self, file_path):
        normalized_path = os.path.normpath(file_path)
        return normalized_path.startswith('.git' + os.sep)


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
                    logging.info(f'Встреча успешно состоялась. статус: {meeting_status}')
                    user_data['current_state'] = 'idle'

                elif response == 'нет':
                    await message.reply("Встреча не состоялась.", reply_markup=ReplyKeyboardRemove())
                    meeting_status = 'DECLINED'
                    await self.meeting_db_manager.update_status(self.confirmation[str(chat_id)]['meeting_id'], meeting_status)
                    del self.meeting_data[self.confirmation[str(chat_id)]['username']]
                    del self.confirmation[str(chat_id)]
                    logging.info(f'Встреча не состоялась. статус: {meeting_status}')
                    user_data['current_state'] = 'idle'

                else:
                    await message.reply("неизвестный ответ")
            else:
                logging.info('handle_confirmation_response: chat_id нет в confirmation')

        except Exception as e:
            logging.info(f"Произошла ошибка handle_confirmation_response: {e}")

    async def backup_password_message(self, message: types.Message, state: FSMContext):
        try:
            password = message.text

            if password == '/cancel':
                await state.finish()
                await message.reply('Команда отменена.')
                return

            if password == f'{DB_PASSWORD}':

                os.environ['PGPASSWORD'] = password

                pg_dump_command = [
                    'pg_dump', '-h', 'unibilim_db_1', '-U', f'{DB_USER}', '-d', f'{DB_NAME}', '-f', 'backup.dump'
                ]
                process = subprocess.run(pg_dump_command, check=True)

                with open('backup.dump', 'rb') as backup_file:
                    await message.reply_document(backup_file, caption="Бэкап успешно выполнен и файл отправлен.")
                    await state.finish()

            else:
                await message.reply("Неверный пароль. Попробуйте еще раз.")

        except subprocess.CalledProcessError as e:
            logging.info(f"Произошла ошибка при создании бэкапа: {e}")
            print(f"Вывод команды: {e.output}")
            await message.reply(
                "Произошла ошибка при создании бэкапа. Пожалуйста, попробуйте позже")

        except Exception as e:
            logging.info(f"Произошла неизвестная ошибка: {e}")
            await message.reply(
                "Произошла ошибка при создании бэкапа. Пожалуйста, попробуйте позже")

        finally:
            os.environ.pop('PGPASSWORD', None)


    async def check_file_name_message(self, message: types.Message, state: FSMContext):
        try:
            if message.text == '/cancel':
                await state.finish()
                await message.reply('Команда отменена.')
                return

            destination_directory = './telegram_bot/garbage'
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)

            project_directory = '.'
            files_in_project = await self.message_services.list_files_in_directory(project_directory)
            filtered_file_list = [file for file in files_in_project if
                                  not await self.message_services.is_git_file(file)]
            file_name = message.text

            if file_name in filtered_file_list:
                source_path = os.path.join(project_directory, file_name)
                copied_file_path = os.path.join(destination_directory, os.path.basename(file_name))
                shutil.copy(source_path, copied_file_path)

                with open(copied_file_path, 'rb') as file:
                    await message.reply_document(file, caption="Файл скопирован и отправлен.")

                shutil.rmtree(destination_directory, ignore_errors=True)

                await state.finish()

            else:
                await message.reply(f"Такого файла нет на сервере!")

        except Exception as e:
            logging.info(f"Произошла ошибка check_file_name_message: {e}")

    async def copy_file_password_message(self, message: types.Message, state: FSMContext):
        try:
            password = message.text

            if password == '/cancel':
                await state.finish()
                await message.reply('Команда отменена.')
                return

            if password == PASSWORD_COPY_FILE:
                await message.answer("Пароль верен. Теперь введите название файла:")
                await state.finish()
                await self.my_state.check_file_name.set()

            else:
                await message.answer(f"Неверный пароль. Попробуйте снова.")

        except Exception as e:
            logging.info(f"Произошла ошибка copy_file_password_message: {e}")

    async def file_name_list_message(self, message: types.Message, state: FSMContext):
        try:

            if message.text == '/cancel':
                await state.finish()
                await message.reply('Команда отменена.')
                return

            if message.text == PASSWORD_NAME_FILE_LIST:
                await message.reply('Команда /cancel может не сработать сразу при /get_file_name. Дождитесь завершения операции для полной отмены.')
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
            logging.info(f"Произошла ошибка file_name_list_message: {e}")

    async def password_reset(self, message: types.Message, state: FSMContext):
        try:
            if message.text == '/cancel':
                await state.finish()
                await message.reply('Команда отменена.')
                return

            await self.db.create_pool()
            url = 'https://backend-prod.unibilim.kg/accounts/password-reset/'

            username = message.chat.username
            new_password = message.text

            user_data = await self.user_db_manager.get_user(username)
            code = await self.user_db_manager.get_reset_password_code(user_data['user__id'])
            token = await self.user_db_manager.get_token(user_data['user__id'])

            data = {
                'user_id': f'{user_data["user__id"]}',
                'code': f'{str(code)}',
                'new_password': f'{str(new_password)}'
            }

            headers = {
                'Authorization': f'Token {token}'
            }

            response = requests.post(url, data=data, headers=headers)

            if response.status_code == 200:
                await message.reply(f"Пароль успешно изменен :)")
                await state.finish()
            else:
                error_data = response.json()
                new_password_errors = error_data.get('errors', {}).get('new_password', [])
                error_messages = ', '.join(
                    new_password_errors) if new_password_errors else "Нет подробной информации об ошибке."
                await message.reply(f"{error_messages}")

        except requests.exceptions.RequestException as req_ex:
            await message.reply("Не удалось отправить запрос на сервер. Пожалуйста, попробуйте позже.")
            await state.finish()

        except Exception as e:
            logging.info(f"Произошла ошибка password_reset: {e}")

    async def password_reset_code(self, message: types.Message, state: FSMContext):
        try:
            if message.text == '/cancel':
                await state.finish()
                await message.reply('Команда отменена.')
                return

            await self.db.create_pool()
            username = message.chat.username
            user_code = message.text

            data = await self.user_db_manager.get_user(username)

            if data:
                correct_code = await self.user_db_manager.get_reset_password_code(data['user__id'])
                if user_code == correct_code:
                    await message.answer(f"Верный код!\nПридумайте новый пароль !")

                    await state.finish()
                    await self.my_state.password_reset.set()

                else:
                    await message.answer("Неверный код. Попробуйте еще раз.")

        except Exception as e:
            logging.info(f"Произошла ошибка password_reset_code: {e}")

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


