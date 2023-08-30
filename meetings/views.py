from rest_framework import viewsets


from .models import Meetings
from .serializers import MeetingsSerializer


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class MeetingsViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingsSerializer    
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        queryset = Meetings.objects.all()
        student_id = self.request.query_params.get('student_id', None)
        professor_id = self.request.query_params.get('professor_id', None)
        if student_id:
            queryset = queryset.filter(student__id=student_id)
        if professor_id:
            queryset = queryset.filter(professor__id=professor_id)
        return queryset


