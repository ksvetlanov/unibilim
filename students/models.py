from django.db import models
from django.contrib.auth.models import User


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts')

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    telegram_username = models.CharField(max_length=255)
    telegram_id = models.CharField(max_length=255, blank=True, null=True)
    phone_numbers = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    district_city = models.ForeignKey(District, on_delete=models.SET_NULL, blank=True, null=True)
    photo = models.ImageField(upload_to='student_photos', blank=True, null=True)
    otp_token = models.CharField(max_length=255)

    status = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.firstname} {self.surname} {self.status} {self.pk}"
