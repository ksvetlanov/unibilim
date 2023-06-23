from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfessorsViewSet, TimetableView, TimetableDetailView

router = DefaultRouter()
router.register('professors', ProfessorsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('timetables/', TimetableView.as_view(), name='timetable-list'),
    path('timetables/<int:pk>/', TimetableDetailView.as_view(), name='timetable-detail'),
]