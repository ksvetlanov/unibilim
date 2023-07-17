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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    patronym = models.CharField(max_length=50, blank=True, null=True)
    info = models.TextField()
    photo = models.ImageField(upload_to='professors/', null=True, blank=True)
    tg_username = models.CharField(max_length=50)
    tg_idbot = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20)
    rate = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)
    price = models.JSONField(null=True, blank=True) # Stores dictionary-like data
    language = models.CharField(max_length=50)
    experience = models.CharField(max_length=5, choices=EXPERIENCE_CHOICES)
    
    def __str__(self):
        return self.firstName + ' ' + self.surname

class Timetable(models.Model):
    professor = models.ForeignKey(Professors, on_delete=models.CASCADE)
    monday = ArrayField(models.TimeField(), blank=True, default=list, null=True)
    tuesday = ArrayField(models.TimeField(), blank=True, default=list, null=True)
    wednesday = ArrayField(models.TimeField(), blank=True, default=list, null=True)
    thursday = ArrayField(models.TimeField(), blank=True, default=list, null=True)
    friday = ArrayField(models.TimeField(), blank=True, default=list, null=True)
    saturday = ArrayField(models.TimeField(), blank=True, default=list, null=True)
    sunday = ArrayField(models.TimeField(), blank=True, default=list, null=True)
    
    def __str__(self):
        return self.professor.firstName + ' ' + self.professor.surname
    
    
class Holiday(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return self.name