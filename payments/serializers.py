from rest_framework import serializers
from .models import Payments

class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'
        


class InitiatePaymentSerializer(serializers.Serializer):
    time_slots = serializers.ListField(child=serializers.ListField(), required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    service = serializers.CharField(max_length=255, required=True)
    professor_id = serializers.IntegerField()
    
class ResponseSerializer(serializers.Serializer):
    format = serializers.CharField(default='xml', read_only=True)
    pg_status = serializers.CharField()
    pg_payment_id = serializers.CharField()
    pg_redirect_url = serializers.CharField()
    pg_redirect_url_type = serializers.CharField()
    pg_salt = serializers.CharField()
    pg_sig = serializers.CharField()
    
    '''
    {
   "service": "Math Tutoring",
   "amount": 10,
   "time_slots": ["2023-07-20T14:30:00", "2023-05-20T14:30:00"],
   "professor_id": 3
}
    
    '''