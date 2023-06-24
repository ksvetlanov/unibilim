from rest_framework import viewsets
from .models import Meetings
from .serializers import MeetingsSerializer

class MeetingsViewSet(viewsets.ModelViewSet):
    queryset = Meetings.objects.all()
    serializer_class = MeetingsSerializer
