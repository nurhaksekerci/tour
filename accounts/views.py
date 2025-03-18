from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserSerializer, UserUpdateSerializer, ChangePasswordSerializer,
    UserProfileSerializer, CustomTokenObtainPairSerializer, RegisterSerializer
)
from .models import CustomUser
from companies.models import Company, Branch

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    JWT token almak için kullanılan endpoint.
    
    Email ve şifre ile giriş yaparak access ve refresh token alır.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="JWT token alın",
        operation_description="Email ve şifre ile JWT token alın",
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
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_summary="Yeni kullanıcı kaydı",
        operation_description="Yeni bir kullanıcı hesabı oluşturun",
        responses={
            201: UserSerializer,
            400: "Geçersiz veri"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user).data,
                "message": "Kullanıcı başarıyla oluşturuldu"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Kullanıcı profili görüntüleme ve güncelleme endpoint'i.
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary="Kullanıcı profili görüntüleme",
        operation_description="Mevcut kullanıcının profil bilgilerini görüntüleyin",
        responses={
            200: UserSerializer,
            401: "Kimlik doğrulama gerekli"
        }
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Kullanıcı profili güncelleme",
        operation_description="Mevcut kullanıcının profil bilgilerini güncelleyin",
        responses={
            200: UserSerializer,
            400: "Geçersiz veri",
            401: "Kimlik doğrulama gerekli"
        }
    )
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    """
    Kullanıcı şifre değiştirme endpoint'i.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary="Şifre değiştirme",
        operation_description="Mevcut kullanıcının şifresini değiştirin",
        request_body=ChangePasswordSerializer,
        responses={
            200: "{'message': 'Şifre başarıyla değiştirildi'}",
            400: "Geçersiz veri",
            401: "Kimlik doğrulama gerekli"
        }
    )
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.validated_data['old_password']):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"message": "Şifre başarıyla değiştirildi"})
            return Response({"error": "Eski şifre yanlış"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    """
    Kullanıcı listesi görüntüleme endpoint'i.
    Yetki seviyesine göre farklı kullanıcıları listeler.
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()

    @swagger_auto_schema(
        operation_summary="Kullanıcı listesi",
        operation_description="Tüm kullanıcıların listesini görüntüleyin",
        manual_parameters=[
            openapi.Parameter(
                'role',
                openapi.IN_QUERY,
                description="Kullanıcı rolüne göre filtrele",
                type=openapi.TYPE_STRING,
                enum=['admin', 'staff', 'user']
            )
        ],
        responses={
            200: UserSerializer(many=True),
            401: "Kimlik doğrulama gerekli"
        }
    )
    def get(self, request, *args, **kwargs):
        role = request.query_params.get('role', None)
        queryset = self.get_queryset()
        if role:
            queryset = queryset.filter(role=role)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CustomTokenVerifyView(TokenVerifyView):
    """
    Token doğrulama ve kullanıcı bilgilerini döndürme endpoint'i.
    """
    
    @swagger_auto_schema(
        operation_summary="Token doğrulama ve kullanıcı bilgileri",
        operation_description="Verilen token'ı doğrular ve kullanıcı bilgilerini döndürür",
        responses={
            200: openapi.Response(
                description="Token geçerli ve kullanıcı bilgileri",
                examples={
                    "application/json": {
                        "token_valid": True,
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "role": "admin",
                            "is_company_admin": True,
                            "is_branch_admin": False
                        }
                    }
                }
            ),
            401: "Geçersiz veya süresi dolmuş token"
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            # Önce standart token doğrulamasını yap
            response = super().post(request, *args, **kwargs)
            
            # Token geçerliyse kullanıcı bilgilerini al
            from rest_framework_simplejwt.tokens import UntypedToken
            from rest_framework_simplejwt.exceptions import InvalidToken
            from django.conf import settings
            import jwt
            
            token = request.data.get('token')
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            
            # User ID'yi al
            user_id = decoded_data.get('user_id')
            user = CustomUser.objects.get(id=user_id)
            
            # Kullanıcı bilgilerini serialize et
            user_data = UserProfileSerializer(user).data
            
            return Response({
                'token_valid': True,
                'user': user_data
            })
            
        except TokenError as e:
            return Response(
                {'token_valid': False, 'error': 'Token geçersiz veya süresi dolmuş'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except CustomUser.DoesNotExist:
            return Response(
                {'token_valid': False, 'error': 'Kullanıcı bulunamadı'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'token_valid': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
