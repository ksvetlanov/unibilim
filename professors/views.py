from rest_framework import viewsets, generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from students.models import Student
from .models import Professors, Timetable, Holiday
from .serializers import ProfessorsSerializer, TimetableSerializer, HolidaysSerializer, ProfessorsMyStudentsSerializer
from meetings.models import Meetings

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
            raise PermissionDenied("Professors matching query does not exist")

        return professor


class ProfessorsMyStudents(generics.ListAPIView):
    serializer_class = ProfessorsMyStudentsSerializer

    def get_queryset(self):
        professor_id = getattr(self.request.user, 'professors', None) and self.request.user.professors.id
        if professor_id is None:
            return Student.objects.none()  # Возвращаем пустой QuerySet

        meetings = Meetings.objects.filter(professor_id=professor_id)
        student_ids = meetings.values_list('student_id', flat=True)
        students = Student.objects.filter(id__in=student_ids)
        return students

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)