from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from professors.models import Professors
from students.models import Student
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

class LoginView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Аутентифицирует пользователя и возвращает токен и роль пользователя.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
        ),
        responses={
            200: openapi.Response(description="Успешная аутентификация", 
                                  schema=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token'),
                                            'role': openapi.Schema(type=openapi.TYPE_STRING, description='Role'),
                                        },
                                    )),
            400: "Invalid Credentials"
        },
    )
    def post(self, request, format=None):
        data = request.data
        username = data.get('username', None)
        password = data.get('password', None)

        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)

        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            response_data = {'token': token.key}

            # Проверка, является ли пользователь профессором или студентом
            try:
                user.professors
                response_data['role'] = 'professor'
                response_data['id'] = user.proffessors.id
            except Professors.DoesNotExist:
                pass

            try:
                user.student
                response_data['role'] = 'student'
                response_data['id'] = user.student.id
            except Student.DoesNotExist:
                pass

            return Response(response_data)
        else:
            return Response({'error': 'Invalid Credentials'},
                            status=status.HTTP_400_BAD_REQUEST)
