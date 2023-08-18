from rest_framework import serializers
from .models import Meetings

class MeetingsSerializer(serializers.ModelSerializer):
    student_firstname = serializers.CharField(source='student.firstname', read_only=True)
    student_lastname = serializers.CharField(source='student.surname', read_only=True)
    professor_firstname = serializers.CharField(source='professor.firstName', read_only=True)
    professor_lastname = serializers.CharField(source='professor.surname', read_only=True)
    professor_info = serializers.CharField(source='professor.info', read_only=True)
    year = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Meetings
        fields = ['datetime','student_firstname','student_lastname','professor_firstname', 'professor_lastname', 'professor_info','day_of_week', 'year', 'month', 'day', 'time', 'jitsiLink','subject']

    def get_year(self, obj):
        return obj.datetime.year

    def get_month(self, obj):
        return obj.datetime.month

    def get_day(self, obj):
        return obj.datetime.day

    def get_time(self, obj):
        return obj.datetime.strftime('%H:%M:%S')  # Форматирование времени в часы:минуты:секунды
