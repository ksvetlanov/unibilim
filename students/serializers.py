from django.core.validators import RegexValidator
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')

    class Meta:
        model = Student
        fields = ['username', 'first_name', 'last_name', 'phone_numbers', 'telegram_id', 'telegram_username', 'city', 'token', 'language']

from rest_framework import serializers

from rest_framework import serializers

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Student

class StudentRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    phone_numbers = serializers.CharField(max_length=20)
    date_of_birth = serializers.DateField()
    region = serializers.ChoiceField(choices=Student.REGION_CHOICES)
    city = serializers.CharField()
    status = serializers.CharField()
    photo = serializers.ImageField()
    otp_token = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Student
        fields = ['username', 'password', 'password2', 'phone_numbers', 'telegram_id', 'telegram_username', 'date_of_birth', 'region', 'city', 'district_city', 'status', 'photo', 'otp_token']

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError("The two password fields didn’t match.")
        data.pop('password2')

        return data

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        user = User.objects.create_user(username=username, password=password)
        validated_data['user'] = user
        student = Student.objects.create(**validated_data)
        return student




class OTPVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)

    def validate_code(self, value):
        return value
