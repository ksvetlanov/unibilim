from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentsViewSet, InitiatePaymentView


router = DefaultRouter()
router.register(r'payments', PaymentsViewSet)


urlpatterns = [
        path('init_payment/', InitiatePaymentView.as_view(), name='init_payment'), 
    path('', include(router.urls)),
]