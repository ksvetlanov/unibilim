FROM python:3.9

WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev musl-dev

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./unibilim .

WORKDIR /app/unibilim

ENV DJANGO_SETTINGS_MODULE=unibilim.settings
RUN python manage.py makemigrations
RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
