from rest_framework import viewsets
from .models import Payments
from .serializers import PaymentsSerializer

class PaymentsViewSet(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer
