from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from professors.models import Professors
from students.models import Student
from .models import PasswordResetCode
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import PasswordResetSerializer


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
                response_data['id'] = user.professors.id
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


class PasswordResetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'user_id': request.user.id})
        if serializer.is_valid():
            user_id = request.user.id
            new_password = serializer.validated_data.get("new_password")
            reset_code = serializer.validated_data.get("code")

            try:
                password_reset_code = PasswordResetCode.objects.get(user_id=user_id, code=reset_code)
            except PasswordResetCode.DoesNotExist:
                return Response({"detail": "Invalid reset code."}, status=status.HTTP_400_BAD_REQUEST)

            user = request.user
            user.password = make_password(new_password)
            user.save()

            password_reset_code.delete()

            return Response({"detail": "Password has been updated successfully."}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid data provided.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
