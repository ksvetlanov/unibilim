from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ProfessorsViewSet, TimetableViewSet

router = routers.DefaultRouter()
router.register(r'professors', ProfessorsViewSet, basename='professors')

professor_router = nested_routers.NestedSimpleRouter(router, r'professors', lookup='professor')
professor_router.register(r'timetable', TimetableViewSet, basename='professor-timetable')

urlpatterns = router.urls + professor_router.urls
