from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from companies.models import City
from companies.serializers import CitySerializer
from .models import (
    VehicleType, BuyerCompany, Tour, NoVehicleTour,
    Transfer, Hotel, Museum, Activity, Guide,
    VehicleSupplier, ActivitySupplier, VehicleCost,
    ActivityCost, HotelPriceHistory, MuseumPriceHistory,
    VehicleCostHistory, ActivityCostHistory
)
from .serializers import (
    VehicleTypeSerializer, BuyerCompanySerializer,
    TourSerializer, NoVehicleTourSerializer, TransferSerializer,
    HotelSerializer, MuseumSerializer, ActivitySerializer,
    GuideSerializer, VehicleSupplierSerializer, ActivitySupplierSerializer,
    VehicleCostSerializer, ActivityCostSerializer,
    HotelPriceHistorySerializer, MuseumPriceHistorySerializer,
    VehicleCostHistorySerializer, ActivityCostHistorySerializer
)

class BaseCompanyViewSet(viewsets.ModelViewSet):
    """
    Temel şirket ViewSet'i.
    Tüm ViewSet'ler için ortak özellikleri içerir.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    pagination_class = None  # Sayfalama kapatıldı
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(company=user.company)

    @swagger_auto_schema(
        operation_summary="Liste",
        operation_description="Kayıtların listesini getirir.",
        responses={
            200: openapi.Response('Başarılı'),
            401: 'Yetkilendirme hatası'
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Detay",
        operation_description="Belirtilen kaydın detaylarını getirir.",
        responses={
            200: openapi.Response('Başarılı'),
            404: 'Kayıt bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Oluştur",
        operation_description="Yeni kayıt oluşturur.",
        responses={
            201: openapi.Response('Başarıyla oluşturuldu'),
            400: 'Geçersiz veri',
            401: 'Yetkilendirme hatası'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Güncelle",
        operation_description="Belirtilen kaydı günceller.",
        responses={
            200: openapi.Response('Başarıyla güncellendi'),
            400: 'Geçersiz veri',
            404: 'Kayıt bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Kısmi Güncelle",
        operation_description="Belirtilen kaydı kısmen günceller.",
        responses={
            200: openapi.Response('Başarıyla güncellendi'),
            400: 'Geçersiz veri',
            404: 'Kayıt bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Sil",
        operation_description="Belirtilen kaydı siler.",
        responses={
            204: 'Başarıyla silindi',
            404: 'Kayıt bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class VehicleTypeViewSet(BaseCompanyViewSet):
    """
    Araç tipleri için API endpoint'leri.
    """
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    search_fields = ['name']
    filterset_fields = ['is_active']
    pagination_class = None  # Sayfalama kapatıldı
class BuyerCompanyViewSet(BaseCompanyViewSet):
    """
    Alıcı şirketler için API endpoint'leri.
    """
    queryset = BuyerCompany.objects.all()
    serializer_class = BuyerCompanySerializer
    search_fields = ['name', 'short_name', 'contact']
    filterset_fields = ['is_active']

class TourViewSet(BaseCompanyViewSet):
    """
    Turlar için API endpoint'leri.
    """
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    search_fields = ['name', 'start_city__name', 'end_city__name']
    filterset_fields = ['start_city', 'end_city', 'is_active']
    pagination_class = None  # Sayfalama kapatıldı


class NoVehicleTourViewSet(BaseCompanyViewSet):
    """
    Araçsız turlar için API endpoint'leri.
    """
    queryset = NoVehicleTour.objects.all()
    serializer_class = NoVehicleTourSerializer
    search_fields = ['name', 'city__name']
    filterset_fields = ['city', 'is_active']
    pagination_class = None  # Sayfalama kapatıldı


class TransferViewSet(BaseCompanyViewSet):
    """
    Transferler için API endpoint'leri.
    """
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    search_fields = ['name', 'start_city__name', 'end_city__name']
    filterset_fields = ['start_city', 'end_city', 'is_active']
    pagination_class = None

class HotelViewSet(BaseCompanyViewSet):
    """
    Oteller için API endpoint'leri.
    """
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    search_fields = ['name', 'city__name']
    filterset_fields = ['city', 'is_active']
    pagination_class = None

    @swagger_auto_schema(
        operation_summary="Fiyat Geçmişi",
        operation_description="Otelin fiyat geçmişini getirir.",
        responses={
            200: HotelPriceHistorySerializer(many=True),
            404: 'Otel bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        hotel = self.get_object()
        history = hotel.price_history.all().order_by('-valid_from')
        serializer = HotelPriceHistorySerializer(history, many=True)
        return Response(serializer.data)

class MuseumViewSet(BaseCompanyViewSet):
    """
    Müzeler için API endpoint'leri.
    """
    queryset = Museum.objects.all()
    serializer_class = MuseumSerializer
    search_fields = ['name', 'city__name']
    filterset_fields = ['city', 'is_active']
    pagination_class = None

    @swagger_auto_schema(
        operation_summary="Fiyat Geçmişi",
        operation_description="Müzenin fiyat geçmişini getirir.",
        responses={
            200: MuseumPriceHistorySerializer(many=True),
            404: 'Müze bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        museum = self.get_object()
        history = museum.price_history.all().order_by('-valid_from')
        serializer = MuseumPriceHistorySerializer(history, many=True)
        return Response(serializer.data)

class ActivityViewSet(BaseCompanyViewSet):
    """
    Aktiviteler için API endpoint'leri.
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    search_fields = ['name']
    filterset_fields = ['cities', 'is_active']
    pagination_class = None

class GuideViewSet(BaseCompanyViewSet):
    """
    Rehberler için API endpoint'leri.
    """
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
    search_fields = ['name', 'phone', 'document_no']
    filterset_fields = ['cities', 'is_active']
    pagination_class = None

class VehicleSupplierViewSet(BaseCompanyViewSet):
    """
    Araç tedarikçileri için API endpoint'leri.
    """
    queryset = VehicleSupplier.objects.all()
    serializer_class = VehicleSupplierSerializer
    search_fields = ['name']
    filterset_fields = ['cities', 'is_active']
    pagination_class = None

class ActivitySupplierViewSet(BaseCompanyViewSet):
    """
    Aktivite tedarikçileri için API endpoint'leri.
    """
    queryset = ActivitySupplier.objects.all()
    serializer_class = ActivitySupplierSerializer
    search_fields = ['name']
    filterset_fields = ['cities', 'is_active']
    pagination_class = None

class VehicleCostViewSet(BaseCompanyViewSet):
    """
    Araç maliyetleri için API endpoint'leri.
    """
    queryset = VehicleCost.objects.all()
    serializer_class = VehicleCostSerializer
    search_fields = ['supplier__name']
    filterset_fields = ['supplier', 'tour', 'transfer', 'is_active']
    pagination_class = None

    @swagger_auto_schema(
        operation_summary="Fiyat Geçmişi",
        operation_description="Araç maliyetinin fiyat geçmişini getirir.",
        responses={
            200: VehicleCostHistorySerializer(many=True),
            404: 'Maliyet kaydı bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        vehicle_cost = self.get_object()
        history = vehicle_cost.price_history.all().order_by('-valid_from')
        serializer = VehicleCostHistorySerializer(history, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Tarih İçin Fiyat",
        operation_description="Belirli bir tarih için araç maliyetini getirir.",
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Fiyat kontrolü için tarih (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True
            )
        ],
        responses={
            200: VehicleCostHistorySerializer,
            400: 'Geçersiz tarih formatı',
            404: 'Fiyat bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    @action(detail=True, methods=['get'])
    def price_for_date(self, request, pk=None):
        vehicle_cost = self.get_object()
        date_str = request.query_params.get('date')
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            price = vehicle_cost.get_price_for_date(target_date)
            if price:
                serializer = VehicleCostHistorySerializer(price)
                return Response(serializer.data)
            return Response({"detail": "Bu tarih için fiyat bulunamadı."}, status=404)
        except ValueError:
            return Response({"detail": "Geçersiz tarih formatı. YYYY-MM-DD kullanın."}, status=400)

class ActivityCostViewSet(BaseCompanyViewSet):
    """
    Aktivite maliyetleri için API endpoint'leri.
    """
    queryset = ActivityCost.objects.all()
    serializer_class = ActivityCostSerializer
    search_fields = ['activity__name', 'supplier__name']
    filterset_fields = ['activity', 'supplier', 'is_active']
    pagination_class = None

    @swagger_auto_schema(
        operation_summary="Fiyat Geçmişi",
        operation_description="Aktivite maliyetinin fiyat geçmişini getirir.",
        responses={
            200: ActivityCostHistorySerializer(many=True),
            404: 'Maliyet kaydı bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        activity_cost = self.get_object()
        history = activity_cost.price_history.all().order_by('-valid_from')
        serializer = ActivityCostHistorySerializer(history, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Tarih İçin Fiyat",
        operation_description="Belirli bir tarih için aktivite maliyetini getirir.",
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Fiyat kontrolü için tarih (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True
            )
        ],
        responses={
            200: ActivityCostHistorySerializer,
            400: 'Geçersiz tarih formatı',
            404: 'Fiyat bulunamadı',
            401: 'Yetkilendirme hatası'
        }
    )
    @action(detail=True, methods=['get'])
    def price_for_date(self, request, pk=None):
        activity_cost = self.get_object()
        date_str = request.query_params.get('date')
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            price = activity_cost.get_price_for_date(target_date)
            if price:
                serializer = ActivityCostHistorySerializer(price)
                return Response(serializer.data)
            return Response({"detail": "Bu tarih için fiyat bulunamadı."}, status=404)
        except ValueError:
            return Response({"detail": "Geçersiz tarih formatı. YYYY-MM-DD kullanın."}, status=400)

class HotelPriceHistoryViewSet(BaseCompanyViewSet):
    """
    Otel fiyat geçmişi için API endpoint'leri.
    """
    queryset = HotelPriceHistory.objects.all()
    serializer_class = HotelPriceHistorySerializer
    filterset_fields = ['hotel', 'currency', 'is_active']
    pagination_class = None

class MuseumPriceHistoryViewSet(BaseCompanyViewSet):
    """
    Müze fiyat geçmişi için API endpoint'leri.
    """
    queryset = MuseumPriceHistory.objects.all()
    serializer_class = MuseumPriceHistorySerializer
    filterset_fields = ['museum', 'currency', 'is_active']
    pagination_class = None

class VehicleCostHistoryViewSet(BaseCompanyViewSet):
    """
    Araç maliyet geçmişi için API endpoint'leri.
    """
    queryset = VehicleCostHistory.objects.all()
    serializer_class = VehicleCostHistorySerializer
    filterset_fields = ['vehicle_cost', 'currency', 'is_active']
    pagination_class = None

class ActivityCostHistoryViewSet(BaseCompanyViewSet):
    """
    Aktivite maliyet geçmişi için API endpoint'leri.
    """
    queryset = ActivityCostHistory.objects.all()
    serializer_class = ActivityCostHistorySerializer
    filterset_fields = ['activity_cost', 'currency', 'is_active']
    pagination_class = None
