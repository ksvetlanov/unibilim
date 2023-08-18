# main.py
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from .settings_bot import TOKEN
from .commands import start_command


# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Регистрируем обработчики команд
dp.register_message_handler(start_command, commands=['start'])

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
