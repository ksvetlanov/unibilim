
from django.urls import path
from .views import LoginView, PasswordResetView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
]
