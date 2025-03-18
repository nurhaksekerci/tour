from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from companies.serializers import CompanyBasicSerializer, BranchBasicSerializer
from .models import CustomUser
from companies.models import Company, Branch

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Token'a özel claims ekle
        token['email'] = user.email
        token['username'] = user.username
        token['role'] = user.role
        token['is_company_admin'] = user.is_company_admin
        token['is_branch_admin'] = user.is_branch_admin
        
        return token

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    branch_detail = BranchBasicSerializer(source='branch', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'password2', 'first_name', 'last_name',
                 'phone', 'gender', 'photo', 'role', 'company', 'branch',
                 'company_detail', 'branch_detail', 'is_company_admin', 'is_branch_admin', 'is_active', 'date_joined')
        extra_kwargs = {
            'company': {'write_only': True},
            'branch': {'write_only': True},
        }
        read_only_fields = ('id', 'is_active', 'date_joined')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone',
                 'gender', 'photo', 'company', 'branch')
        read_only_fields = ('email',)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski şifre yanlış")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    branch_detail = BranchBasicSerializer(source='branch', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                 'phone', 'gender', 'photo', 'role', 'company_detail',
                 'branch_detail', 'is_company_admin', 'is_branch_admin',
                 'date_joined', 'last_login')
        read_only_fields = ('id', 'is_active', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user