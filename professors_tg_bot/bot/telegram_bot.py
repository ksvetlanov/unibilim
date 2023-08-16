import asyncio
import asyncpg
from aiogram import Bot
from datetime import datetime
from ..meetings.models import Meetings


# Параметры подключения к базе данных и токен бота
DB_USER = 'postgres'
DB_PASSWORD = '290111208dj'
DB_NAME = 'unibilim'
DB_HOST = 'localhost'
BOT_TOKEN = '6111157752:AAGokr4olAmmwSTz0ygY8omJHcXappx7NOA'

# Создание экземпляра бота
bot = Bot(token=BOT_TOKEN)


async def send_scheduled_links():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

    while True:
        try:
            now = datetime.now()
            # Получение всех запланированных встреч
            scheduled_meetings = await Meetings.objects.filter(status='PENDING', datetime__lte=now).all()

            for meeting in scheduled_meetings:
                student_id = meeting.student.id
                link = meeting.jitsiLink

                try:
                    await bot.send_message(chat_id=student_id, text=f"Ваша встреча: {link}")
                    # Обновление статуса встречи
                    meeting.status = 'ACCEPTED'
                    await meeting.update()
                except Exception as e:
                    print(f"Ошибка при отправке ссылки: {e}")
        except Exception as e:
            print(f"Ошибка при выполнении запроса к базе данных: {e}")

        await asyncio.sleep(60)  # Пауза между проверками


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_scheduled_links())
    loop.run_forever()
