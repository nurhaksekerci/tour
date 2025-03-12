from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleTypeViewSet, BuyerCompanyViewSet,
    TourViewSet, NoVehicleTourViewSet, TransferViewSet,
    HotelViewSet, MuseumViewSet, ActivityViewSet,
    GuideViewSet, VehicleSupplierViewSet, ActivitySupplierViewSet,
    VehicleCostViewSet, ActivityCostViewSet,
    HotelPriceHistoryViewSet, MuseumPriceHistoryViewSet,
    VehicleCostHistoryViewSet, ActivityCostHistoryViewSet
)

app_name = 'records'

router = DefaultRouter()

# Ana modeller için router kayıtları
router.register(r'vehicle-types', VehicleTypeViewSet)
router.register(r'buyer-companies', BuyerCompanyViewSet)
router.register(r'tours', TourViewSet)
router.register(r'no-vehicle-tours', NoVehicleTourViewSet)
router.register(r'transfers', TransferViewSet)
router.register(r'hotels', HotelViewSet)
router.register(r'museums', MuseumViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'guides', GuideViewSet)
router.register(r'vehicle-suppliers', VehicleSupplierViewSet)
router.register(r'activity-suppliers', ActivitySupplierViewSet)
router.register(r'vehicle-costs', VehicleCostViewSet)
router.register(r'activity-costs', ActivityCostViewSet)

# Fiyat geçmişi için router kayıtları
router.register(r'hotel-price-history', HotelPriceHistoryViewSet)
router.register(r'museum-price-history', MuseumPriceHistoryViewSet)
router.register(r'vehicle-cost-history', VehicleCostHistoryViewSet)
router.register(r'activity-cost-history', ActivityCostHistoryViewSet)

urlpatterns = [
    # Özel endpoint'ler buraya eklenebilir
    path('hotels/<int:pk>/price-history/',
         HotelViewSet.as_view({'get': 'price_history'}),
         name='hotel-price-history'),
         
    path('museums/<int:pk>/price-history/',
         MuseumViewSet.as_view({'get': 'price_history'}),
         name='museum-price-history'),
         
    path('vehicle-costs/<int:pk>/price-history/',
         VehicleCostViewSet.as_view({'get': 'price_history'}),
         name='vehicle-cost-price-history'),
         
    path('activity-costs/<int:pk>/price-history/',
         ActivityCostViewSet.as_view({'get': 'price_history'}),
         name='activity-cost-price-history'),
] + router.urls 