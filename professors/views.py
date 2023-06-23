from rest_framework import viewsets, generics
from .models import Professors, Timetable
from .serializers import ProfessorsSerializer, TimetableSerializer

class ProfessorsViewSet(viewsets.ModelViewSet):
    queryset = Professors.objects.all()
    serializer_class = ProfessorsSerializer
    
    
class TimetableView(generics.ListCreateAPIView):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

class TimetableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer