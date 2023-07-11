from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Meetings
from .serializers import MeetingsSerializer

class MeetingsViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingsSerializer

    def get_queryset(self):
        queryset = Meetings.objects.all()
        professor_id = self.request.query_params.get('professor_id', None)
        student_id = self.request.query_params.get('student_id', None)
        
        if professor_id is not None:
            queryset = queryset.filter(professor_id=professor_id)
            
        if student_id is not None:
            queryset = queryset.filter(student_id=student_id)
            
        return queryset
