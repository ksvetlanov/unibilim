from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import PasswordResetCode


class PasswordResetSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=4)
    new_password = serializers.CharField(required=True)

    def validate_code(self, value):
        user_id = self.context['user_id']
        try:
            user = User.objects.get(id=user_id)
            reset_code = PasswordResetCode.objects.get(user=user, code=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError("Invalid reset code")

        return value

    def validate_new_password(self, value):

        try:
            validate_password(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(str(e))

        return value