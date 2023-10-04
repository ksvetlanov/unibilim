from rest_framework import viewsets


from .models import Meetings
from .serializers import MeetingsSerializer
from datetime import datetime

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class MeetingsViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingsSerializer    
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        queryset = Meetings.objects.all()
        student_id = self.request.query_params.get('student_id', None)
        professor_id = self.request.query_params.get('professor_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if student_id:
            queryset = queryset.filter(student__id=student_id)
        if professor_id:
            queryset = queryset.filter(professor__id=professor_id)

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(datetime__date__gte=parsed_start_date)
            except ValueError:
                pass

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(datetime__date__lte=parsed_end_date)
            except ValueError:
                pass

        return queryset
