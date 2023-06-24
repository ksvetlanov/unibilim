from rest_framework import serializers
from .models import Meetings

class MeetingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meetings
        fields = ['id', 'student', 'professor', 'datetime', 'jitsiLink', 'status', 'duration']
