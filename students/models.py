from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    patronym = models.CharField(max_length=255, blank=True, null=True)
    telegram_username = models.CharField(max_length=255)
    telegram_id = models.CharField(max_length=255)
    phone_numbers = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    REGION_CHOICES = [
        ('region1', 'Край 1'),
        ('region2', 'Край 2'),
        ('region3', 'Край 3'),
        # Добавьте остальные края по аналогии
    ]
    region = models.CharField(max_length=255, choices=REGION_CHOICES)
    city = models.CharField(max_length=255)
    district_city = models.CharField(max_length=255)  # Добавленное поле
    status = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='student_photos', null=True)
    otp_token = models.CharField(max_length=255)
    token = models.CharField(max_length=32, null=True)
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.firstname + ' ' + self.surname
