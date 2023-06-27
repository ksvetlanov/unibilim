from rest_framework import serializers
from .models import Professors, Timetable
import datetime 
from django.contrib.auth.models import User


class ProfessorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professors
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True}
        }

    def create(self, validated_data):
        # получение данных пользователя
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)

        # создание профессора с созданным пользователем
        professor = Professors.objects.create(user=user, **validated_data)
        return professor
        
class TimetableSerializer(serializers.ModelSerializer):
    start_time_monday = serializers.TimeField(write_only=True)
    end_time_monday = serializers.TimeField(write_only=True)
    start_time_tuesday = serializers.TimeField(write_only=True)
    end_time_tuesday = serializers.TimeField(write_only=True)
    start_time_wednesday = serializers.TimeField(write_only=True)
    end_time_wednesday = serializers.TimeField(write_only=True)
    start_time_thursday = serializers.TimeField(write_only=True)
    end_time_thursday = serializers.TimeField(write_only=True)
    start_time_friday = serializers.TimeField(write_only=True)
    end_time_friday = serializers.TimeField(write_only=True)
    start_time_saturday = serializers.TimeField(write_only=True)
    end_time_saturday = serializers.TimeField(write_only=True)
    start_time_sunday = serializers.TimeField(write_only=True)
    end_time_sunday = serializers.TimeField(write_only=True)

    class Meta:
        model = Timetable
        fields = '__all__'

    def create(self, validated_data):
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day in days_of_week:
            start_time = datetime.datetime.strptime(validated_data.pop(f'start_time_{day}'), "%H:%M").time()
            end_time = datetime.datetime.strptime(validated_data.pop(f'end_time_{day}'), "%H:%M").time()

            # Переведите начало и конец времени в часы рабочего дня
            hours_in_day = int((datetime.datetime.combine(datetime.date.today(), end_time) - 
                                datetime.datetime.combine(datetime.date.today(), start_time)).seconds / 3600)
            workday_hours = [datetime.time(hour=(start_time.hour + i) % 24) for i in range(hours_in_day)]

            # Сохраните часы работы для данного дня недели
            validated_data[day] = workday_hours

        return super().create(validated_data)

