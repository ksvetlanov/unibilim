from django.urls import path
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ProfessorsViewSet, TimetableViewSet, HolidaysViewSet, CabinetView, ProfessorsMyStudents, DeviceTokenView

router = routers.DefaultRouter()
router.register(r'professors', ProfessorsViewSet, basename='professors')
router.register(r'holidays', HolidaysViewSet, basename='holidays')


urlpatterns = [
    path('api/save_device_token/', DeviceTokenView.as_view(), name='save-device-token'),
    path('professors/cabinet/', CabinetView.as_view(), name='professors_cabinet-view'),
    path('professors/my_students/', ProfessorsMyStudents.as_view(), name='professors_my_students-view'),
] + router.urls


professor_router = nested_routers.NestedSimpleRouter(router, r'professors', lookup='professor')
professor_router.register(r'timetable', TimetableViewSet, basename='professor-timetable')

urlpatterns += professor_router.urls