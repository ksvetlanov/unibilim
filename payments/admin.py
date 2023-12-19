from django.contrib import admin
from .models import Payments
# Register your models here.
class PaymentsAdmin(admin.ModelAdmin):
    # Список полей, которые будут отображаться в админке
    list_display = (
        'id',
        'amount',
        'datetime',
        'student',
        'professor',
        'description',
        'service',
        'time_slots',)
    # например, list_filter, search_fields и т.д.

# Зарегистрируйте модель с использованием определенного администратора
admin.site.register(Payments, PaymentsAdmin)