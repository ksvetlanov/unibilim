from rest_framework import viewsets


from .models import Meetings
from .serializers import MeetingsSerializer


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class MeetingsViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingsSerializer    
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student'):
            return Meetings.objects.filter(student=user.student)
        elif hasattr(user, 'professor'):
            return Meetings.objects.filter(professor=user.professor)
        else:
            return Meetings.objects.none() 

