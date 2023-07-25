from django.contrib import admin
from .models import Student,District,City,Region
# Register your models here.
admin.site.register(Student)
admin.site.register(Region)
admin.site.register(District)
admin.site.register(City)
