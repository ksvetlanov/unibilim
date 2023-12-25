from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentRegistrationAPIView, OTPVerificationView, RegionListView, DistrictListView, CityListView,StudentMeetingsView, ResendOTPView, monitor_meetings_view


# router = DefaultRouter()
# router.register(r'students', StudentViewSet)
# router.register(r'professors', ProfessorViewSet)

urlpatterns = [
    path('monitor-meetings/', monitor_meetings_view, name='monitor_meetings'),
    # path('', include(router.urls)),
    path('register/student/', StudentRegistrationAPIView.as_view(), name='student_register'),
    path('verify/otp/', OTPVerificationView.as_view(), name='otp_verification'),
    path('verify/', ResendOTPView.as_view(), name='verification'),
    path('regions/', RegionListView.as_view(), name='region-list'),
    path('regions/<int:region_id>/districts/', DistrictListView.as_view(), name='district-list'),
    path('districts/<int:district_id>/cities/', CityListView.as_view(), name='city-list'),
    path('api/student/meetings/', StudentMeetingsView.as_view(), name='student-meetings'),


]

