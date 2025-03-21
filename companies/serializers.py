from rest_framework import serializers
from .models import (
    Currency, City, District, Neighborhood, Plan, Company, Branch,
    Subscription, Usage, Payment, APIKey, APIUsage,
    Notification, AuditLog, Integration
)
import uuid
from drf_yasg.utils import swagger_serializer_method

class CurrencySerializer(serializers.ModelSerializer):
    """
    Para birimi için temel serializer.
    Tüm para birimi bilgilerini içerir.
    """
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']
        read_only_fields = ['id']

    def validate_code(self, value):
        """
        Para birimi kodunun 3 karakterli ve büyük harf olduğunu kontrol eder.
        """
        if len(value) != 3:
            raise serializers.ValidationError("Para birimi kodu 3 karakter olmalıdır.")
        return value.upper()

    def validate_symbol(self, value):
        """
        Sembolün boş olmadığını kontrol eder.
        """
        if not value.strip():
            raise serializers.ValidationError("Sembol boş olamaz.")
        return value

class CurrencyListSerializer(serializers.ModelSerializer):
    """
    Para birimi listesi için özet serializer.
    Sadece temel bilgileri içerir.
    """
    class Meta:
        model = Currency
        fields = ['id', 'code', 'symbol']
        read_only_fields = ['id']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    city_detail = CitySerializer(source='city', read_only=True)

    class Meta:
        model = District
        fields = ('id', 'name', 'city', 'city_detail', 'code')

class NeighborhoodSerializer(serializers.ModelSerializer):
    district_detail = DistrictSerializer(source='district', read_only=True)

    class Meta:
        model = Neighborhood
        fields = ('id', 'name', 'district', 'district_detail', 'code')

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class PlanDetailSerializer(serializers.ModelSerializer):
    active_companies_count = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = '__all__'

    def get_active_companies_count(self, obj):
        return obj.companies.filter(is_active=True).count()

# Basit Company Serializer (accounts app için)
class CompanyBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'email', 'phone', 'is_active')

# Basit Branch Serializer (accounts app için)
class BranchBasicSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Branch
        fields = ('id', 'name', 'company_name', 'email', 'phone')

class CompanyListSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    current_plan_name = serializers.CharField(source='current_plan.name', read_only=True)
    branches_count = serializers.SerializerMethodField()
    active_users_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ('id', 'name', 'city_name', 'current_plan_name', 'is_active',
                 'branches_count', 'active_users_count', 'created_at')

    def get_branches_count(self, obj):
        return obj.branches.count()

    def get_active_users_count(self, obj):
        return obj.users.filter(is_active=True).count()

class CompanyDetailSerializer(serializers.ModelSerializer):
    city_detail = CitySerializer(source='city', read_only=True)
    district_detail = DistrictSerializer(source='district', read_only=True)
    neighborhood_detail = NeighborhoodSerializer(source='neighborhood', read_only=True)
    current_plan_detail = PlanSerializer(source='current_plan', read_only=True)
    branches_count = serializers.SerializerMethodField()
    active_users_count = serializers.SerializerMethodField()
    storage_usage_gb = serializers.SerializerMethodField()
    main_branch_id = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('tenant_id',)
        extra_kwargs = {
            'tax_number': {'required': False, 'allow_blank': True}
        }

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField())
    def get_main_branch_id(self, obj):
        # Eğer create sırasında oluşturulduysa
        if hasattr(self, 'main_branch_id'):
            return self.main_branch_id
        # Mevcut instance için merkez şubeyi bul
        main_branch = obj.branches.filter(name="Merkez").first()
        return main_branch.id if main_branch else None

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField())
    def get_branches_count(self, obj):
        return obj.branches.count()

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField())
    def get_active_users_count(self, obj):
        return obj.users.filter(is_active=True).count()

    @swagger_serializer_method(serializer_or_field=serializers.FloatField())
    def get_storage_usage_gb(self, obj):
        return round(obj.storage_usage / (1024 * 1024 * 1024), 2)

    def create(self, validated_data):
        """
        Yeni bir şirket oluşturur ve otomatik olarak merkez şubesi oluşturur.
        
        İşlem sırası:
        1. Benzersiz bir tenant_id oluşturulur
        2. Şirket kaydı oluşturulur
        3. Merkez şubesi oluşturulur:
           - İsim: "Merkez"
           - Email: merkez@[şirket-email-domain]
           - Diğer bilgiler şirket bilgileriyle aynı
           - Durum: active
        """
        # Tenant ID oluştur
        validated_data['tenant_id'] = uuid.uuid4()
        
        # Şirketi oluştur
        company = super().create(validated_data)
        
        # Merkez şubesi oluştur
        main_branch = Branch.objects.create(
            company=company,
            name="Merkez",
            email=f"merkez@{company.email.split('@')[1]}",  # Şirket email'inden domain kısmını al
            phone=company.phone,
            address=company.address,
            city=company.city,
            district=company.district,
            neighborhood=company.neighborhood,
            status='active'
        )
        
        # Merkez şube ID'sini instance'a ekle
        self.main_branch_id = main_branch.id
        
        return company

class BranchListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = ('id', 'name', 'company_name', 'city_name', 'users_count', 'created_at')

    def get_users_count(self, obj):
        return obj.users.count()

class BranchDetailSerializer(serializers.ModelSerializer):
    company_detail = CompanyListSerializer(source='company', read_only=True)
    city_detail = CitySerializer(source='city', read_only=True)
    district_detail = DistrictSerializer(source='district', read_only=True)
    neighborhood_detail = NeighborhoodSerializer(source='neighborhood', read_only=True)
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = '__all__'

    def get_users_count(self, obj):
        return obj.users.count()

class SubscriptionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True, allow_null=True)

    class Meta:
        model = Subscription
        fields = '__all__'

class UsageSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Usage
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    subscription_detail = SubscriptionSerializer(source='subscription', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ('id', 'company', 'key_name', 'is_active', 'expires_at',
                 'last_used_at', 'created_at', 'updated_at')
        read_only_fields = ('api_key',)

class APIUsageSerializer(serializers.ModelSerializer):
    api_key_name = serializers.CharField(source='api_key.key_name', read_only=True)

    class Meta:
        model = APIUsage
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'

class IntegrationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Integration
        fields = '__all__'
        extra_kwargs = {
            'config': {'write_only': True}  # Güvenlik için config bilgilerini sadece yazılabilir yap
        } 