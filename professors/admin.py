from django.contrib import admin
from .models import Professors, Timetable, Holiday
# Register your models here.
admin.site.register(Professors)
admin.site.register(Timetable)
admin.site.register(Holiday)