from aiogram import types
import random
from .settings_bot import LINK_TO_WEBSITE


class CommandServices:

    async def generate_code(self):
        return ''.join(random.choice('0123456789') for _ in range(4))


class CommandHandler:
    def __init__(self, bot, dp, database, user_db_manager, professor_db_manager, student_db_manager, meeting_db_manager, my_state):
        self.bot = bot
        self.dp = dp
        self.db = database
        self.user_db_manager = user_db_manager
        self.professor_db_manager = professor_db_manager
        self.student_db_manager = student_db_manager
        self.meeting_db_manager = meeting_db_manager
        self.command_services = CommandServices()
        self.my_state = my_state
        self.active_users = set()
        self.codes = {}

    async def start_command(self, message: types.Message):
        await self.db.create_pool()
        user = message.from_user
        username = message.chat.username
        try:
            data = await self.user_db_manager.get_user(username)

            if data:
                if data['user_type'] == 'professor':
                    await self.professor_db_manager.update_chat_id(data['username'], user.id)
                    await message.reply(f"Привет {data['username']} Я буду напоминать вам о предстоящих встречах и присылать ссылки в назначенное время, где будут проводиться занятия.")
                    self.active_users.add(username)
                    print(f'Активные пользователи : {len(self.active_users)}')

                elif data['user_type'] == 'student':
                    await self.student_db_manager.update_chat_id(data['username'], user.id)
                    await message.reply(f"Привет {data['username']} Я буду напоминать вам о предстоящих встречах и присылать ссылки в назначенное время, где будут проводиться занятия.")
                    self.active_users.add(username)
                    print(f'активные пользователи : {len(self.active_users)}')

            else:
                await message.answer(f"Пользователь не найден в базе данных. Посетите этот сайт: {LINK_TO_WEBSITE}")

        except Exception as e:
            print(f"Произошла ошибка start_command: {e}")

    async def backup_command(self, message: types.Message):
        await message.reply("Пожалуйста, введите пароль от базы данных.")
        await self.my_state.backup_password.set()

    async def copy_file_command(self, message: types.Message):
        await message.reply('Пожалуйста, введите пароль')
        await self.my_state.copy_file_password.set()

    async def file_name_command(self, message: types.Message):
        await message.reply('Пожалуйста, введите пароль')
        await self.my_state.file_name_list_password.set()

    async def password_reset_command(self, message: types.Message):
        await self.db.create_pool()
        username = message.chat.username
        try:
            data = await self.user_db_manager.get_user(username)
            if data:
                code = await self.command_services.generate_code()
                await self.user_db_manager.create_reset_password_code(data['user__id'], code)
                db_code = await self.user_db_manager.get_reset_password_code(data['user__id'])
                await message.reply(f'Ваш код для сброса пароля : {db_code}')
                await self.my_state.password_reset_code.set()

        except Exception as e:
            print(f"Произошла ошибка password_reset_command: {e}")

    async def register_commands(self):
        self.dp.register_message_handler(self.start_command, commands=['start'])
        self.dp.register_message_handler(self.backup_command, commands=['backup'])
        self.dp.register_message_handler(self.copy_file_command, commands=['get_file'])
        self.dp.register_message_handler(self.file_name_command, commands=['get_file_name'])
        self.dp.register_message_handler(self.password_reset_command, commands=['password_reset'])



















