FROM python:3.9

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./unibilim .

WORKDIR /app/unibilim

ENV DJANGO_SETTINGS_MODULE=unibilim.settings

CMD ["python", "../manage.py", "runserver", "0.0.0.0:80"]
