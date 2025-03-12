from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OperationViewSet, OperationCustomerViewSet,
    OperationSalesPriceViewSet, OperationDayViewSet,
    OperationItemViewSet, OperationSubItemViewSet
)

app_name = 'operations'

router = DefaultRouter()

# Ana modeller için router kayıtları
router.register(r'operations', OperationViewSet)
router.register(r'customers', OperationCustomerViewSet)
router.register(r'sales-prices', OperationSalesPriceViewSet)
router.register(r'days', OperationDayViewSet)
router.register(r'items', OperationItemViewSet)
router.register(r'subitems', OperationSubItemViewSet)

urlpatterns = [
    # Özel endpoint'ler buraya eklenebilir
    path('operations/<int:pk>/update-status/',
         OperationViewSet.as_view({'post': 'update_status'}),
         name='operation-update-status'),
         
    path('items/<int:pk>/calculate-cost/',
         OperationItemViewSet.as_view({'get': 'calculate_cost'}),
         name='item-calculate-cost'),
         
    path('subitems/<int:pk>/calculate-cost/',
         OperationSubItemViewSet.as_view({'get': 'calculate_cost'}),
         name='subitem-calculate-cost'),
] + router.urls 