from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Currency, City, District, Neighborhood, Plan, Company, Branch,
    Subscription, Usage, Payment, APIKey, APIUsage,
    Notification, AuditLog, Integration
)

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')
    search_fields = ('code', 'name')
    ordering = ('code',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'code')
    list_filter = ('city',)
    search_fields = ('name', 'code', 'city__name')
    ordering = ('city', 'name')

@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'code')
    list_filter = ('district__city', 'district')
    search_fields = ('name', 'code', 'district__name')
    ordering = ('district', 'name')

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'is_active')
    list_filter = ('plan_type', 'is_active')
    search_fields = ('name',)
    ordering = ('price',)

admin.site.register(Company)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'phone', 'city', 'status')
    list_filter = ('company', 'status', 'city')
    search_fields = ('name', 'email', 'phone', 'company__name')
    ordering = ('company', 'name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'plan', 'start_date', 'end_date', 'status', 'subscription_type')
    list_filter = ('status', 'subscription_type', 'plan')
    search_fields = ('company__name',)
    ordering = ('-start_date',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ('company', 'feature', 'value', 'date')
    list_filter = ('company', 'feature', 'date')
    search_fields = ('company__name',)
    ordering = ('-date',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'payment_date', 'payment_method', 'is_paid')
    list_filter = ('payment_method', 'is_paid', 'payment_date')
    search_fields = ('subscription__company__name',)
    ordering = ('-payment_date',)
    readonly_fields = ('created_at',)

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('company', 'key_name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('company__name', 'key_name')
    ordering = ('-created_at',)
    readonly_fields = ('api_key', 'created_at')

@admin.register(APIUsage)
class APIUsageAdmin(admin.ModelAdmin):
    list_display = ('api_key', 'endpoint', 'method', 'status_code', 'created_at')
    list_filter = ('method', 'status_code', 'endpoint')
    search_fields = ('api_key__company__name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('company', 'type', 'title', 'priority', 'is_read', 'created_at')
    list_filter = ('type', 'priority', 'is_read')
    search_fields = ('company__name', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'action', 'model_name', 'created_at')
    list_filter = ('action', 'model_name')
    search_fields = ('company__name', 'user__email', 'details')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ('company', 'integration_type', 'provider', 'status', 'updated_at')
    list_filter = ('integration_type', 'provider', 'status')
    search_fields = ('company__name',)
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')
