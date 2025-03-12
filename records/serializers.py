from rest_framework import serializers
from .models import (
    VehicleType, City, BuyerCompany, Tour, NoVehicleTour,
    Transfer, Hotel, Museum, Activity, Guide,
    VehicleSupplier, ActivitySupplier, VehicleCost,
    ActivityCost, HotelPriceHistory, MuseumPriceHistory,
    VehicleCostHistory, ActivityCostHistory
)
from companies.serializers import CompanyBasicSerializer, CurrencySerializer, CitySerializer
from django.utils import timezone

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'


class BuyerCompanySerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)

    class Meta:
        model = BuyerCompany
        fields = '__all__'

class TourSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    start_city_detail = CitySerializer(source='start_city', read_only=True)
    end_city_detail = CitySerializer(source='end_city', read_only=True)

    class Meta:
        model = Tour
        fields = '__all__'

class NoVehicleTourSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    city_detail = CitySerializer(source='city', read_only=True)

    class Meta:
        model = NoVehicleTour
        fields = '__all__'

class TransferSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    start_city_detail = CitySerializer(source='start_city', read_only=True)
    end_city_detail = CitySerializer(source='end_city', read_only=True)

    class Meta:
        model = Transfer
        fields = '__all__'

class HotelSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    city_detail = CitySerializer(source='city', read_only=True)
    currency_detail = CurrencySerializer(source='currency', read_only=True)
    current_price = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = '__all__'

    def get_current_price(self, obj):
        current_price = obj.get_price_for_date(timezone.now().date())
        if current_price:
            return {
                'single_price': current_price.single_price,
                'double_price': current_price.double_price,
                'triple_price': current_price.triple_price,
                'currency': current_price.currency.code
            }
        return None

class MuseumSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    city_detail = CitySerializer(source='city', read_only=True)
    currency_detail = CurrencySerializer(source='currency', read_only=True)
    current_price = serializers.SerializerMethodField()

    class Meta:
        model = Museum
        fields = '__all__'

    def get_current_price(self, obj):
        current_price = obj.get_price_for_date(timezone.now().date())
        if current_price:
            return {
                'local_price': current_price.local_price,
                'foreign_price': current_price.foreign_price,
                'currency': current_price.currency.code
            }
        return None

class ActivitySerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    cities_detail = CitySerializer(source='cities', many=True, read_only=True)

    class Meta:
        model = Activity
        fields = '__all__'

class GuideSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    cities_detail = CitySerializer(source='cities', many=True, read_only=True)

    class Meta:
        model = Guide
        fields = '__all__'

class VehicleSupplierSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    cities_detail = CitySerializer(source='cities', many=True, read_only=True)

    class Meta:
        model = VehicleSupplier
        fields = '__all__'

class ActivitySupplierSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    cities_detail = CitySerializer(source='cities', many=True, read_only=True)

    class Meta:
        model = ActivitySupplier
        fields = '__all__'

class VehicleCostSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    supplier_detail = VehicleSupplierSerializer(source='supplier', read_only=True)
    tour_detail = TourSerializer(source='tour', read_only=True)
    transfer_detail = TransferSerializer(source='transfer', read_only=True)
    currency_detail = CurrencySerializer(source='currency', read_only=True)
    current_price = serializers.SerializerMethodField()

    class Meta:
        model = VehicleCost
        fields = '__all__'

    def get_current_price(self, obj):
        current_price = obj.get_price_for_date(timezone.now().date())
        if current_price:
            return {
                'car_cost': current_price.car_cost,
                'minivan_cost': current_price.minivan_cost,
                'minibus_cost': current_price.minibus_cost,
                'midibus_cost': current_price.midibus_cost,
                'bus_cost': current_price.bus_cost,
                'currency': current_price.currency.code
            }
        return None

class ActivityCostSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    activity_detail = ActivitySerializer(source='activity', read_only=True)
    supplier_detail = ActivitySupplierSerializer(source='supplier', read_only=True)
    currency_detail = CurrencySerializer(source='currency', read_only=True)
    current_price = serializers.SerializerMethodField()

    class Meta:
        model = ActivityCost
        fields = '__all__'

    def get_current_price(self, obj):
        current_price = obj.get_price_for_date(timezone.now().date())
        if current_price:
            return {
                'price': current_price.price,
                'currency': current_price.currency.code
            }
        return None

# Fiyat Geçmişi Serializer'ları
class HotelPriceHistorySerializer(serializers.ModelSerializer):
    currency_detail = CurrencySerializer(source='currency', read_only=True)

    class Meta:
        model = HotelPriceHistory
        fields = '__all__'

class MuseumPriceHistorySerializer(serializers.ModelSerializer):
    currency_detail = CurrencySerializer(source='currency', read_only=True)

    class Meta:
        model = MuseumPriceHistory
        fields = '__all__'

class VehicleCostHistorySerializer(serializers.ModelSerializer):
    currency_detail = CurrencySerializer(source='currency', read_only=True)

    class Meta:
        model = VehicleCostHistory
        fields = '__all__'

class ActivityCostHistorySerializer(serializers.ModelSerializer):
    currency_detail = CurrencySerializer(source='currency', read_only=True)

    class Meta:
        model = ActivityCostHistory
        fields = '__all__' 