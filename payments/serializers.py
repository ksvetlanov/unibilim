from rest_framework import serializers
from .models import Payments

class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'


class InitiatePaymentSerializer(serializers.Serializer):
    time_slots = serializers.ListField(child=serializers.DictField(), required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    service = serializers.CharField(max_length=255, required=True)