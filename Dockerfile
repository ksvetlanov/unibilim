FROM python:3.9

WORKDIR /app

# Установка зависимостей для psycopg2-binary
RUN apt-get update \
    && apt-get install -y libpq-dev gcc python3-dev musl-dev \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main" >> /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y postgresql-client-16 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Установка зависимостей Python
RUN pip install -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=unibilim.settings

CMD ["bash", "-c", "python manage.py runserver 0.0.0.0:80 & python -m telegram_bot.main"]
