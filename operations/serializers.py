from rest_framework import serializers
from .models import (
    Operation, OperationCustomer, OperationSalesPrice,
    OperationDay, OperationItem, OperationSubItem
)
from companies.serializers import (
    CompanyBasicSerializer, BranchBasicSerializer, CurrencySerializer
)
from records.serializers import (
    BuyerCompanySerializer, TourSerializer, TransferSerializer,
    ActivitySerializer, MuseumSerializer, HotelSerializer,
    GuideSerializer, VehicleTypeSerializer, VehicleSupplierSerializer,
    ActivitySupplierSerializer, VehicleCostSerializer, ActivityCostSerializer,
    NoVehicleTourSerializer
)
from accounts.serializers import UserSerializer

class OperationCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationCustomer
        fields = '__all__'

class OperationSalesPriceSerializer(serializers.ModelSerializer):
    currency_detail = CurrencySerializer(source='currency', read_only=True)

    class Meta:
        model = OperationSalesPrice
        fields = '__all__'

class OperationSubItemSerializer(serializers.ModelSerializer):
    tour_detail = TourSerializer(source='tour', read_only=True)
    transfer_detail = TransferSerializer(source='transfer', read_only=True)
    museums_detail = MuseumSerializer(source='museums', many=True, read_only=True)
    hotel_detail = HotelSerializer(source='hotel', read_only=True)
    guide_detail = GuideSerializer(source='guide', read_only=True)
    activity_detail = ActivitySerializer(source='activity', read_only=True)
    activity_supplier_detail = ActivitySupplierSerializer(source='activity_supplier', read_only=True)
    activity_cost_detail = ActivityCostSerializer(source='activity_cost', read_only=True)
    sales_currency_detail = CurrencySerializer(source='sales_currency', read_only=True)
    cost_currency_detail = CurrencySerializer(source='cost_currency', read_only=True)

    class Meta:
        model = OperationSubItem
        fields = '__all__'

class OperationItemSerializer(serializers.ModelSerializer):
    vehicle_type_detail = VehicleTypeSerializer(source='vehicle_type', read_only=True)
    vehicle_supplier_detail = VehicleSupplierSerializer(source='vehicle_supplier', read_only=True)
    vehicle_cost_detail = VehicleCostSerializer(source='vehicle_cost', read_only=True)
    no_vehicle_tour_detail = NoVehicleTourSerializer(source='no_vehicle_tour', read_only=True)
    no_vehicle_activity_detail = ActivitySerializer(source='no_vehicle_activity', read_only=True)
    activity_supplier_detail = ActivitySupplierSerializer(source='activity_supplier', read_only=True)
    activity_cost_detail = ActivityCostSerializer(source='activity_cost', read_only=True)
    sales_currency_detail = CurrencySerializer(source='sales_currency', read_only=True)
    cost_currency_detail = CurrencySerializer(source='cost_currency', read_only=True)
    subitems = OperationSubItemSerializer(many=True, read_only=True)

    class Meta:
        model = OperationItem
        fields = '__all__'

class OperationDaySerializer(serializers.ModelSerializer):
    items = OperationItemSerializer(many=True, read_only=True)

    class Meta:
        model = OperationDay
        fields = '__all__'

class OperationListSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    branch_detail = BranchBasicSerializer(source='branch', read_only=True)
    buyer_company_detail = BuyerCompanySerializer(source='buyer_company', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    follow_by_detail = UserSerializer(source='follow_by', read_only=True)

    class Meta:
        model = Operation
        fields = [
            'id', 'company', 'company_detail', 'branch', 'branch_detail',
            'buyer_company', 'buyer_company_detail', 'created_by', 'created_by_detail',
            'follow_by', 'follow_by_detail', 'reference_number', 'start_date',
            'end_date', 'status', 'total_pax', 'created_at', 'is_active'
        ]

class OperationDetailSerializer(serializers.ModelSerializer):
    company_detail = CompanyBasicSerializer(source='company', read_only=True)
    branch_detail = BranchBasicSerializer(source='branch', read_only=True)
    buyer_company_detail = BuyerCompanySerializer(source='buyer_company', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    follow_by_detail = UserSerializer(source='follow_by', read_only=True)
    customers = OperationCustomerSerializer(many=True, read_only=True)
    sales_prices = OperationSalesPriceSerializer(many=True, read_only=True)
    days = OperationDaySerializer(many=True, read_only=True)

    class Meta:
        model = Operation
        fields = '__all__' 