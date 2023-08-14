from rest_framework import serializers
from .models import Professors, Timetable, Holiday
import datetime 
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')  # и любые другие поля, которые вы хотите включить
        extra_kwargs = {
            'password': {'write_only': True}
        }


class ProfessorsSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # использование вложенного сериализатора

    class Meta:
        model = Professors
        fields = '__all__'
        

    def create(self, validated_data):
        # получение данных пользователя
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)

        # создание профессора с созданным пользователем
        professor = Professors.objects.create(user=user, **validated_data)
        return professor
 
        
class TimetableSerializer(serializers.ModelSerializer):
    start_time_monday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    end_time_monday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    start_time_tuesday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    end_time_tuesday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    start_time_wednesday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    end_time_wednesday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    start_time_thursday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    end_time_thursday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    start_time_friday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    end_time_friday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    start_time_saturday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    end_time_saturday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    start_time_sunday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])
    end_time_sunday = serializers.TimeField(write_only=True, required=False, allow_null=True, format='%H:%M', input_formats=['%H:%M',])

    class Meta:
        model = Timetable
        fields = '__all__'

    def create(self, validated_data):
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day in days_of_week:
            start_time = validated_data.pop(f'start_time_{day}', None)
            end_time = validated_data.pop(f'end_time_{day}', None)

            if start_time and end_time:               
                workday_hours = [start_time, end_time]          
                validated_data[day] = workday_hours
            else:
                validated_data[day] = None

        return super().create(validated_data)


class HolidaysSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Holiday
        fields = '__all__'


class ProfessorsCabinetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professors
        fields = '__all__'

