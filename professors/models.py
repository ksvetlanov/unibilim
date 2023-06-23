from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

class Professors(models.Model):
    EXPERIENCE_CHOICES = [
        ('1-3', '1-3 years'),
        ('3-5', '3-5 years'),
        ('5-10', '5-10 years'),
        ('10+', 'More than 10 years'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    patronym = models.CharField(max_length=50, blank=True)
    info = models.TextField()
    photo = models.ImageField(upload_to='professors/')
    tg_username = models.CharField(max_length=50)
    tg_idbot = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=20)
    rate = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    price = models.JSONField() # Stores dictionary-like data
    language = models.CharField(max_length=50)
    experience = models.CharField(max_length=5, choices=EXPERIENCE_CHOICES)

class Timetable(models.Model):
    professor = models.ForeignKey(Professors, on_delete=models.CASCADE)
    monday = ArrayField(models.TimeField(), blank=True, default=list)
    tuesday = ArrayField(models.TimeField(), blank=True, default=list)
    wednesday = ArrayField(models.TimeField(), blank=True, default=list)
    thursday = ArrayField(models.TimeField(), blank=True, default=list)
    friday = ArrayField(models.TimeField(), blank=True, default=list)
    saturday = ArrayField(models.TimeField(), blank=True, default=list)
    sunday = ArrayField(models.TimeField(), blank=True, default=list)