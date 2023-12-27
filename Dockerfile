FROM python:3.9

WORKDIR /app

RUN apt-get update \
    && apt-get install -y libpq-dev gcc python3-dev musl-dev \

RUN apt-get update \
    && apt-get install -y postgresql-client=16.1-1.pgdg120+1 \
    && rm -rf /var/lib/apt/lists/*

COPY  . .

RUN pip install -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=unibilim.settings

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]

