from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CurrencyViewSet, CityViewSet, DistrictViewSet, NeighborhoodViewSet,
    PlanViewSet, CompanyViewSet, BranchViewSet,
    SubscriptionViewSet, UsageViewSet, PaymentViewSet,
    APIKeyViewSet, APIUsageViewSet, NotificationViewSet,
    AuditLogViewSet, IntegrationViewSet
)

app_name = 'companies'

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet)
router.register(r'cities', CityViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'neighborhoods', NeighborhoodViewSet)
router.register(r'plans', PlanViewSet)
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'usages', UsageViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'api-keys', APIKeyViewSet)
router.register(r'api-usages', APIUsageViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'integrations', IntegrationViewSet)

urlpatterns = [
    # Özel endpoint'ler buraya eklenebilir
    path('companies/<int:pk>/statistics/', 
         CompanyViewSet.as_view({'get': 'statistics'}), 
         name='company-statistics'),
    
    path('companies/<int:pk>/usage-report/',
         CompanyViewSet.as_view({'get': 'usage_report'}),
         name='company-usage-report'),
         
    path('branches/<int:pk>/statistics/',
         BranchViewSet.as_view({'get': 'statistics'}),
         name='branch-statistics'),
] + router.urls 