from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingsViewSet

router = DefaultRouter()
router.register(r'meetings', MeetingsViewSet, basename='meetings')


urlpatterns = [
    path('', include(router.urls)),
]