from rest_framework import viewsets, generics
from .models import Professors, Timetable
from .serializers import ProfessorsSerializer, TimetableSerializer

class ProfessorsViewSet(viewsets.ModelViewSet):
    queryset = Professors.objects.all()
    serializer_class = ProfessorsSerializer
    lookup_field = 'id'

class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer

    def get_queryset(self):
        queryset = Timetable.objects.filter(professor__id=self.kwargs['professor_id'])
        return queryset
