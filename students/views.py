from rest_framework import serializers
import requests
from rest_framework.response import Response
from .serializers import StudentRegisterSerializer, OTPVerificationSerializer, RegionSerializer, DistrictSerializer, \
    CitySerializer
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.views import APIView
import json
from .models import Student, District, Region

from rest_framework import generics
from .models import Region, District, City
from .serializers import RegionSerializer, DistrictSerializer, CitySerializer
from rest_framework.permissions import AllowAny

class RegionListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class DistrictListView(generics.ListAPIView):
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        region_id = self.kwargs['region_id']
        return District.objects.filter(region__id=region_id)

class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        district_id = self.kwargs['district_id']
        return City.objects.filter(district__id=district_id)
def save_token_to_server(transaction_id, token):
    try:
        student = Student.objects.get(user__username=transaction_id)
        student.otp_token = token
        print(token)
        print(student.otp_token)
        student.save()
    except Student.DoesNotExist:
        raise serializers.ValidationError("Неверный идентификатор транзакции")


def get_token_from_server(transaction_id):
    try:
        student = Student.objects.get(user__username=transaction_id)
        return student.otp_token
    except Student.DoesNotExist:
        return None


def send_otp_code(transaction_id, phone):
    url = 'https://smspro.nikita.kg/api/otp/send'
    api_key = '92503b1a8d4f6e0e30de3cf9e4e35919'

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    data = {
        'transaction_id': transaction_id,
        'phone': phone
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = response.json()

    if response.status_code == 200 and response_data.get('status') == 0:
        token = response_data.get('token')
        print(token)
        save_token_to_server(transaction_id, token)
        return token
    else:
        raise Exception('Failed to send OTP')


def verify_otp_code(token, code):
    url = 'https://smspro.nikita.kg/api/otp/verify'
    api_key = '92503b1a8d4f6e0e30de3cf9e4e35919'

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    data = {
        'token': token,
        'code': code
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = response.json()

    if response.status_code == 200 and response_data.get('status') == 0:
        return True
    else:
        return False


class StudentRegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = StudentRegisterSerializer


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            student = serializer.save()


            transaction_id = serializer.validated_data['username']
            token = student.otp_token
            # print("transaction_id:", transaction_id)
            # print("token:", token)
            save_token_to_server(transaction_id, token)

            # Отправка одноразового пароля
            phone = serializer.validated_data['phone_numbers']
            send_otp_code(transaction_id, phone)


            request.session['transaction_id'] = transaction_id

            # Перенаправление на страницу подтверждения кода
            return redirect('otp_verification')
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = 'https://smspro.nikita.kg/api/otp/verify'
        api_key = '92503b1a8d4f6e0e30de3cf9e4e35919'

        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }


        session = SessionStore(request.session.session_key)
        transaction_id = session.get('transaction_id')
        token = get_token_from_server(transaction_id)

        data = {
            'token': token,
            'code': serializer.validated_data['code']
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        print(response_data)

        if response_data.get('status') == 0 and response_data.get('description') == 'Valid Code':
            transaction_id = session.get('transaction_id')
            student = Student.objects.get(user__username=transaction_id)  # Находим объект Student по transaction_id
            student.status = True
            student.save()  # Обновляем статус на True

            return Response({'message': 'Проверка успешна. Статус пользователя обновлен на True.'})
        else:
            return Response({'message': 'Проверка неуспешна'}, status=status.HTTP_400_BAD_REQUEST)

         # return Response(response_data)
