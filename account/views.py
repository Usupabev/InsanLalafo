from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import *


class RegistrationView(APIView):
    def post(self, request):
        data = request.data
        serializers = RegisterSerializer(data=data)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response('Вы Успешно зарегестрировались!', status=status.HTTP_201_CREATED)
        return Response('Не валидна', status=status.HTTP_400_BAD_REQUEST)

class ActivateView(APIView):
    def get(self, request, activation_code):
        User = get_user_model()
        user = get_object_or_404(User, activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Ваш аккаунт успешно активирован', status=status.HTTP_200_OK)

class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response('Successfully logged out', status=status.HTTP_200_OK)

class ForgotPassword(APIView):
    def get(self, request):
        email = request.query_params.get('email')
        user = get_object_or_404(MyUser, email=email)
        user.is_active = False
        user.create_activation_code()
        user.save()
        send_activation_code(email=email, activation_code=user.activation_code)
        return Response('Вам отправлено письмо', status=200)

class ForgotPasswordComplete(APIView):
    def post(self, request):
        serializer = CreateNewPasswordSerialzier(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Вы успешно восстановили пароль', status.HTTP_200_OK)

