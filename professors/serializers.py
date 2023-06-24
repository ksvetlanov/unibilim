from rest_framework import serializers
from .models import Professors, Timetable

class ProfessorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professors
        fields = '__all__'
        
class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'