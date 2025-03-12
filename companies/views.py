from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    Currency, City, District, Neighborhood, Plan, Company, Branch,
    Subscription, Usage, Payment, APIKey, APIUsage,
    Notification, AuditLog, Integration
)
from .serializers import (
    CurrencySerializer, CurrencyListSerializer,
    CitySerializer, DistrictSerializer, NeighborhoodSerializer,
    PlanSerializer, PlanDetailSerializer,
    CompanyListSerializer, CompanyDetailSerializer,
    BranchListSerializer, BranchDetailSerializer,
    SubscriptionSerializer, UsageSerializer, PaymentSerializer,
    APIKeySerializer, APIUsageSerializer, NotificationSerializer,
    AuditLogSerializer, IntegrationSerializer
)
from .permissions import (
    IsCompanyAdmin, IsBranchAdmin, IsCompanyMember,
    CanManageCompany, CanManageBranch
)

# Create your views here.

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'code']
    filterset_fields = ['name', 'code']

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'code', 'city__name']
    filterset_fields = ['city', 'name', 'code']

class NeighborhoodViewSet(viewsets.ModelViewSet):
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'code', 'district__name']
    filterset_fields = ['district', 'name', 'code']

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'plan_type']
    filterset_fields = ['plan_type', 'is_active']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlanDetailSerializer
        return PlanSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    """
    Şirket yönetimi için API endpoint'leri.
    
    * Şirket oluşturma, güncelleme, silme işlemleri
    * Şirket detaylarını görüntüleme
    * Şirket istatistiklerini alma
    * Kullanım raporları oluşturma
    """
    serializer_class = CompanyDetailSerializer
    permission_classes = [IsAuthenticated, CanManageCompany]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'tax_number', 'email']
    filterset_fields = ['is_active', 'current_plan', 'city']
    queryset = Company.objects.none()  # Varsayılan boş queryset

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Company.objects.all()
        elif user.is_company_admin:
            return Company.objects.filter(id=user.company.id)
        return Company.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'statistics']:
            return CompanyListSerializer
        return CompanyDetailSerializer

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        company = self.get_object()
        stats = {
            'total_branches': company.branches.count(),
            'active_users': company.users.filter(is_active=True).count(),
            'storage_usage_gb': round(company.storage_usage / (1024 * 1024 * 1024), 2),
            'active_subscriptions': company.subscriptions.filter(is_active=True).count(),
        }
        return Response(stats)

    @action(detail=True, methods=['get'])
    def usage_report(self, request, pk=None):
        company = self.get_object()
        # Kullanım raporu mantığı burada implement edilecek
        return Response({'message': 'Usage report will be implemented'})

class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchDetailSerializer
    permission_classes = [IsAuthenticated, CanManageBranch]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'email', 'company__name']
    filterset_fields = ['company', 'city']
    queryset = Branch.objects.none()  # Varsayılan boş queryset

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Branch.objects.all()
        elif user.is_company_admin:
            return Branch.objects.filter(company=user.company)
        elif user.is_branch_admin:
            return Branch.objects.filter(id=user.branch.id)
        return Branch.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return BranchListSerializer
        return BranchDetailSerializer

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        branch = self.get_object()
        stats = {
            'total_users': branch.users.count(),
            'active_users': branch.users.filter(is_active=True).count(),
        }
        return Response(stats)

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['company', 'plan', 'status', 'subscription_type']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Subscription.objects.all()
        return Subscription.objects.filter(company=user.company)

class UsageViewSet(viewsets.ModelViewSet):
    queryset = Usage.objects.all()
    serializer_class = UsageSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['company', 'feature', 'date']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Usage.objects.all()
        return Usage.objects.filter(company=user.company)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['subscription', 'payment_method', 'is_paid']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(subscription__company=user.company)

class APIKeyViewSet(viewsets.ModelViewSet):
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return APIKey.objects.all()
        return APIKey.objects.filter(company=user.company)

class APIUsageViewSet(viewsets.ModelViewSet):
    queryset = APIUsage.objects.all()
    serializer_class = APIUsageSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['api_key', 'endpoint', 'method', 'status_code']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return APIUsage.objects.all()
        return APIUsage.objects.filter(api_key__company=user.company)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['type', 'priority', 'is_read']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Notification.objects.all()
        return Notification.objects.filter(company=user.company)

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['action', 'model_name', 'user']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AuditLog.objects.all()
        return AuditLog.objects.filter(company=user.company)

class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['integration_type', 'provider', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Integration.objects.all()
        return Integration.objects.filter(company=user.company)

class CurrencyViewSet(viewsets.ModelViewSet):
    """
    Para birimi işlemleri için API endpoint'leri.
    
    list:
        Tüm para birimlerini listeler.
        
    create:
        Yeni bir para birimi oluşturur.
        
    retrieve:
        Belirtilen para biriminin detaylarını getirir.
        
    update:
        Belirtilen para birimini günceller.
        
    delete:
        Belirtilen para birimini siler.
    """
    queryset = Currency.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['code', 'name']
    filterset_fields = ['code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CurrencyListSerializer
        return CurrencySerializer
    
    @swagger_auto_schema(
        operation_description="Para birimi listesini getirir",
        responses={
            200: CurrencyListSerializer(many=True),
            401: "Yetkilendirme hatası"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Yeni para birimi oluşturur",
        request_body=CurrencySerializer,
        responses={
            201: CurrencySerializer,
            400: "Geçersiz veri",
            401: "Yetkilendirme hatası"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
