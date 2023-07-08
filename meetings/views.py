from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Meetings
from .serializers import MeetingsSerializer

class MeetingsViewSet(viewsets.ModelViewSet):
    queryset = Meetings.objects.all()
    serializer_class = MeetingsSerializer

    @action(detail=False, methods=['post'])
    def by_professor(self, request):
        professor_id = request.data.get('professor_id')
        meetings = self.queryset.filter(professor_id=professor_id)
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)
