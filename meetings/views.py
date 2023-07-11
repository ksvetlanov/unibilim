from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Meetings
from .serializers import MeetingsSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class MeetingsViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingsSerializer

    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'professor_id', openapi.IN_QUERY, description="ID of the professor",
            type=openapi.TYPE_INTEGER),
        openapi.Parameter(
            'student_id', openapi.IN_QUERY, description="ID of the student",
            type=openapi.TYPE_INTEGER),
        openapi.Parameter(
            'ordering', openapi.IN_QUERY, description="Order of the results",
            type=openapi.TYPE_STRING)
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Meetings.objects.all()
        professor_id = self.request.query_params.get('professor_id', None)
        student_id = self.request.query_params.get('student_id', None)

        if professor_id is not None:
            queryset = queryset.filter(professor__id=professor_id)

        if student_id is not None:
            queryset = queryset.filter(student__id=student_id)

        return queryset

