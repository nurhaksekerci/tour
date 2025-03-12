from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserSerializer, UserUpdateSerializer, ChangePasswordSerializer,
    UserProfileSerializer, CustomTokenObtainPairSerializer
)

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    JWT token almak için kullanılan endpoint.
    
    Email ve şifre ile giriş yaparak access ve refresh token alır.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Email ve şifre ile JWT token alır",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Kullanıcı email adresi'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Kullanıcı şifresi'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Başarılı giriş",
                examples={
                    "application/json": {
                        "access": "access_token_here",
                        "refresh": "refresh_token_here"
                    }
                }
            ),
            401: "Geçersiz kimlik bilgileri"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class RegisterView(generics.CreateAPIView):
    """
    Yeni kullanıcı kaydı için endpoint.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Yeni kullanıcı kaydı oluşturur",
        request_body=UserSerializer,
        responses={
            201: UserSerializer,
            400: "Geçersiz veri"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Kullanıcı profili görüntüleme ve güncelleme endpoint'i.
    """
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Kullanıcı profil bilgilerini getirir",
        responses={
            200: UserProfileSerializer,
            401: "Kimlik doğrulama hatası"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Kullanıcı profil bilgilerini günceller",
        request_body=UserUpdateSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Geçersiz veri",
            401: "Kimlik doğrulama hatası"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

class ChangePasswordView(generics.UpdateAPIView):
    """
    Kullanıcı şifre değiştirme endpoint'i.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Kullanıcı şifresini değiştirir",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(
                description="Başarılı",
                examples={
                    "application/json": {
                        "message": "Şifre başarıyla değiştirildi"
                    }
                }
            ),
            400: "Geçersiz şifre",
            401: "Kimlik doğrulama hatası"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class UserListView(generics.ListAPIView):
    """
    Kullanıcı listesi görüntüleme endpoint'i.
    Yetki seviyesine göre farklı kullanıcıları listeler.
    """
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Yetki seviyesine göre kullanıcı listesi getirir",
        manual_parameters=[
            openapi.Parameter(
                'role',
                openapi.IN_QUERY,
                description="Kullanıcı rolü filtresi",
                type=openapi.TYPE_STRING,
                enum=['admin', 'company_admin', 'branch_admin', 'employee'],
                required=False
            )
        ],
        responses={
            200: UserProfileSerializer(many=True),
            401: "Kimlik doğrulama hatası"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
