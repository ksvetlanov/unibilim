from .models import Region, District, City
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')

    class Meta:
        model = Student
        fields = ['username', 'first_name', 'last_name','patronym', 'phone_numbers', 'telegram_id', 'telegram_username', 'city',
                  'token', 'otp_token', 'language']


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class StudentRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    firstname = serializers.CharField()
    surname = serializers.CharField()
    patronym = serializers.CharField(allow_blank=True, required=False)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    phone_numbers = serializers.CharField(max_length=20)
    telegram_username = serializers.CharField()
    date_of_birth = serializers.DateField(input_formats=['%d-%m-%Y'])
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())
    district_city = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    # photo = serializers.ImageField()

    class Meta:
        model = Student
        fields = ['username','firstname','surname','patronym', 'password', 'password2', 'phone_numbers', 'telegram_username', 'date_of_birth', 'region',
                  'district_city', 'city', 'photo']

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


