from rest_framework import viewsets, generics
from rest_framework.exceptions import PermissionDenied
from .models import Professors, Timetable, Holiday
from .serializers import ProfessorsSerializer, TimetableSerializer, HolidaysSerializer


class ProfessorsViewSet(viewsets.ModelViewSet):
    queryset = Professors.objects.all()
    serializer_class = ProfessorsSerializer
    lookup_field = 'id'


class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Timetable.objects.none()
        queryset = Timetable.objects.filter(professor__id=self.kwargs['professor_id'])
        return queryset


class HolidaysViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaysSerializer
    lookup_field = 'id'


class CabinetView(generics.RetrieveAPIView):
    queryset = Professors.objects.all()
    serializer_class = ProfessorsSerializer


    def get_object(self):
        user = self.request.user
        try:
            professor = self.queryset.get(user=user)
        except Professors.DoesNotExist:
            raise PermissionDenied("Professor matching query does not exist")

        return professor
