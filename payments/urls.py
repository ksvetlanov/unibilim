from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentsViewSet, InitiatePaymentView #PaymentResultView


router = DefaultRouter()
router.register(r'payments', PaymentsViewSet)


urlpatterns = [
    path('init_payment/', InitiatePaymentView.as_view(), name='init_payment'), 
    #path('check_payment/', PaymentResultView.as_view(), name='check_payment'), 
    path('', include(router.urls)),
]