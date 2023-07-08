FROM python:3.9

WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev musl-dev

COPY  . .


RUN pip install -r unibilim/requirements.txt





ENV DJANGO_SETTINGS_MODULE=unibilim.settings
RUN python unibilim/manage.py makemigrations
RUN python unibilim/manage.py migrate

CMD ["python", "unibilim/manage.py", "runserver", "0.0.0.0:80"]
