from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .models import User
from django.forms import ValidationError
from django.views.decorators.csrf import csrf_exempt
import re

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt import views as jwt_views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    SignUpSerializer,
    LoginTokenSerializer,
    ChangePasswordSerializer
)
from rest_framework import generics

import requests


# RESTFRAMEWORK VIEWS...
class LoginView(jwt_views.TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = LoginTokenSerializer


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # checking old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def custom_validate_password_token(request, token):
    resp = requests.post(
        'http://3.139.124.188/customers/password_reset/validate_token/',
        data={'token': token}
    )

    try:
        response_json = resp.json()
    except:
        response_json = {}
    status = response_json.get("status", "FAILED")
    return Response({"status": status}, status=200 if status == "OK" else 400)


@csrf_exempt
def login_view(request):
    status = None
    status_code = None
    url = None
    message = ''
    data = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        data = {
            'username': username,
            'password': password,
            'payload': request.POST
        }
        if user is not None:
            if user.is_active:
                login(request, user)
                url = 'http://3.139.124.188/customers/home/'
                status = True
                status_code = 200
        else:
            url = None
            status = False
            message = 'Invalid Username or Password'
            status_code = 401

    return JsonResponse({'redirection_url': url, 'success': status, 'message': message, 'data': data},
                        status=status_code)


def logout_view(request):
    logout(request)
    return JsonResponse({'redirection_url': 'http://3.139.124.188/customers/login/'}, status=200)


@csrf_exempt
def signup_view(request):
    message = ''
    url = None
    status = None
    status_code = None

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            # raise ValidationError("Invalid email format")
            message = "Invalid email format"
            status_code = 400

        if password != password2:
            # raise ValidationError("Passwords miss match")
            message = "Passwords not matched correctly"
            status_code = 400

        user = User(username=username, email=email)
        user.set_password(password2)
        user.save()
        url = "http://3.139.124.188/customers/login/"
        status_code = 200

    return JsonResponse({
        'redirection_url': url, 'success': status, 'message': message
    }, status=status_code)


def username_validation(request, username):
    if User.objects.filter(username=username).exists():
        return JsonResponse({"message": "Username not available", "available": False})
    return JsonResponse({"message": "Username valid", "available": True})
