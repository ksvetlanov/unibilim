from rest_framework import serializers
from .serializers import StudentRegisterSerializer
import json
from .models import Region, District, City
from .serializers import RegionSerializer, DistrictSerializer, CitySerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.sessions.backends.db import SessionStore
import requests
from rest_framework import generics
from .models import Student
from rest_framework.permissions import IsAuthenticated
from meetings.models import Meetings
from .serializers import MeetingsSerializerStudent
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime

def generate_transaction_id(username):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d%H%M")    

    return f"{username}{formatted_datetime}"


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')

        if not username:
            return Response({'message': 'Требуется имя пользователя.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(user__username=username)
        except Student.DoesNotExist:
            return Response({'message': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if student.status:
            return Response({'message': 'Пользователь уже подтвержден.'}, status=status.HTTP_400_BAD_REQUEST)

        phone = student.phone_numbers 
        try:
            send_otp_code(generate_transaction_id(username), phone)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP успешно отправлен.'}, status=status.HTTP_200_OK)


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
    api_key = '17cd096ba91b288e64ed6512661cb010'

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
        save_token_to_server(transaction_id[:-12], token)
        return token
    else:
        error_message = f"Failed to send OTP. Response status code: {response.status_code}."
        if response_data.get('status') is not None:
            error_message += f" Server status: {response_data.get('status')}."
        if response_data.get('error_message'):
            error_message += f" Error details: {response_data.get('error_message')}."
        raise Exception(error_message)



def verify_otp_code(token, code):
    url = 'https://smspro.nikita.kg/api/otp/verify'
    api_key = '17cd096ba91b288e64ed6512661cb010'

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
            save_token_to_server(transaction_id, token)
            phone = serializer.validated_data['phone_numbers']
            send_otp_code(generate_transaction_id(transaction_id), phone)
            request.session['transaction_id'] = transaction_id

            student = Student.objects.get(user__username=transaction_id)
            token = student.otp_token
            # Отправить токен вместе с сообщением об успешной регистрации
            return Response({
                "message": "Student created successfully.",
                "token": token  # Включаем токен в ответ
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        code = request.data.get('code')

        if not token or not code:
            return Response({'message': 'Token and code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        url = 'https://smspro.nikita.kg/api/otp/verify'
        api_key = '17cd096ba91b288e64ed6512661cb010'

        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        try:
            student = Student.objects.get(otp_token=token)
        except Student.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'token': token,
            'code': code
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        print(response_data)

        if response_data.get('status') == 0 and response_data.get('description') == 'Valid Code':
            student.status = True
            student.save()

            return Response({'message': 'Проверка успешна. Статус пользователя обновлен на True.'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Проверка неуспешна'}, status=status.HTTP_400_BAD_REQUEST)



class StudentMeetingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = request.user.student
        meetings = Meetings.objects.filter(student=student)

        serializer = MeetingsSerializerStudent(meetings, many=True)
        return Response(serializer.data)


from datetime import datetime
from django.utils import timezone
from firebase_admin import messaging
from meetings.models import Meetings

def send_today_meeting_notifications():
        print("JR")
        now = timezone.now()
        today = now.date()  # Текущая дата
    # Найдите все встречи, запланированные на сегодня
        today_meetings = Meetings.objects.filter(datetime__date=today, status='PENDING')

        for meeting in today_meetings:
        # Отправьте уведомление на устройство профессора
            message = messaging.Message(
            notification=messaging.Notification(
                title='Занятие сегодня',
                body=f'У вас запланировано занятие на сегодня!'
            ),
            token=meeting.professor.user.professors.device_token,  # Поле с device_token профессора
        )

        try:
            response = messaging.send(message)
            # Уведомление успешно отправлено, можно обновить статус встречи
            meeting.status = 'ACCEPTED'
            meeting.save()
        except Exception as e:
            print(f"Ошибка при отправке уведомления: {e}")

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from firebase_admin import messaging
from meetings.models import Meetings

# Создайте функцию, которая будет выполняться при добавлении новой записи (встречи) в базу данных
@receiver(post_save, sender=Meetings)
def send_notification_on_new_meeting(sender, instance, created, **kwargs):
    if created:
        # Если создана новая запись (встреча), отправьте уведомление преподавателю
        message = messaging.Message(
            notification=messaging.Notification(
                title='Новая встреча',
                body=f'У вас новая встреча!'
            ),
            token=instance.professor.user.professors.device_token,  # Замените на поле с device_token профессора
        )

        try:
            response = messaging.send(message)
        except Exception as e:
            # Обработка ошибки отправки уведомления
            print(f"Ошибка при отправке уведомления: {e}")

from django.http import HttpResponse
def monitor_meetings_view(request):
    send_today_meeting_notifications()
    return HttpResponse("Скрипт успешно выполнен.")
