from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentRegistrationAPIView, OTPVerificationView

# router = DefaultRouter()
# router.register(r'students', StudentViewSet)
# router.register(r'professors', ProfessorViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('register/student/', StudentRegistrationAPIView.as_view(), name='student_register'),
    path('verify/otp/', OTPVerificationView.as_view(), name='otp_verification'),
]

