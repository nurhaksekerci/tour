from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True, verbose_name="Para Birimi Kodu")  # USD, EUR, TRY
    name = models.CharField(max_length=50, verbose_name="Para Birimi Adı")  # US Dollar, Euro, Turkish Lira
    symbol = models.CharField(max_length=5, verbose_name="Sembol")  # $, €, ₺

    class Meta:
        verbose_name = "Para Birimi"
        verbose_name_plural = "Para Birimleri"

    def __str__(self):
        return f"{self.code} ({self.symbol})"

class City(models.Model):
    name = models.CharField(_("City Name"), max_length=100, unique=True)
    code = models.CharField(_("City Code"), max_length=10, unique=True, validators=[MinLengthValidator(2), MaxLengthValidator(10)])

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(_("District Name"), max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts')
    code = models.CharField(_("District Code"), max_length=10, validators=[MinLengthValidator(2), MaxLengthValidator(10)])

    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("Districts")
        unique_together = ('city', 'name')

    def __str__(self):
        return f"{self.name}, {self.city.name}"

class Neighborhood(models.Model):
    name = models.CharField(_("Neighborhood Name"), max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='neighborhoods')
    code = models.CharField(_("Neighborhood Code"), max_length=10, validators=[MinLengthValidator(2), MaxLengthValidator(10)])

    class Meta:
        verbose_name = _("Neighborhood")
        verbose_name_plural = _("Neighborhoods")
        unique_together = ('district', 'name')

    def __str__(self):
        return f"{self.name}, {self.district.name}"

class Plan(models.Model):
    PLAN_TYPES = (
        ('free', _('Free')),
        ('starter', _('Starter')),
        ('professional', _('Professional')),
        ('enterprise', _('Enterprise')),
    )

    name = models.CharField(_("Plan Name"), max_length=100)
    plan_type = models.CharField(_("Plan Type"), max_length=20, choices=PLAN_TYPES)
    description = models.TextField(_("Description"))
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    max_users = models.IntegerField(_("Maximum Users"))
    max_storage = models.IntegerField(_("Maximum Storage (GB)"))
    max_branches = models.IntegerField(_("Maximum Branches"))
    features = models.JSONField(_("Features"), default=dict)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")

    def __str__(self):
        return f"{self.name} - {self.get_plan_type_display()}"

class Company(models.Model):
    name = models.CharField(_("Company Name"), max_length=255, unique=True)
    tax_number = models.CharField(_("Tax Number"), max_length=20, unique=True)
    address = models.TextField(_("Address"))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='companies')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='companies')
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.SET_NULL, null=True, blank=True, related_name='companies')
    phone = models.CharField(_("Phone Number"), max_length=20)
    email = models.EmailField(_("Email Address"), unique=True)
    website = models.URLField(_("Website"), blank=True, null=True)
    tenant_id = models.UUIDField(_("Tenant ID"), unique=True, db_index=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    storage_usage = models.BigIntegerField(_("Storage Usage (bytes)"), default=0)
    current_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='companies')
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.name

class Branch(models.Model):
    STATUS_CHOICES = (
        ('active', _('Aktif')),
        ('inactive', _('Pasif')),
        ('pending', _('Onay Bekliyor')),
        ('suspended', _('Askıya Alındı')),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='branches',
        verbose_name=_('Şirket')
    )
    name = models.CharField(_('Şube Adı'), max_length=255)
    email = models.EmailField(_('E-posta'), unique=True)
    phone = models.CharField(_('Telefon'), max_length=20)
    address = models.TextField(_('Adres'))
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        related_name='branches',
        verbose_name=_('Şehir')
    )
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        related_name='branches',
        verbose_name=_('İlçe')
    )
    neighborhood = models.ForeignKey(
        Neighborhood,
        on_delete=models.SET_NULL,
        null=True,
        related_name='branches',
        verbose_name=_('Mahalle')
    )
    status = models.CharField(
        _('Durum'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Şube')
        verbose_name_plural = _('Şubeler')
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"

class Subscription(models.Model):
    SUBSCRIPTION_TYPES = (
        ('monthly', _('Monthly')),
        ('yearly', _('Yearly')),
        ('custom', _('Custom')),
    )

    STATUS_CHOICES = (
        ('active', _('Active')),
        ('pending', _('Pending')),
        ('cancelled', _('Cancelled')),
        ('expired', _('Expired')),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subscriptions')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='subscriptions', null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    subscription_type = models.CharField(_("Subscription Type"), max_length=10, choices=SUBSCRIPTION_TYPES)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    is_active = models.BooleanField(_("Is Active"), default=True)
    is_auto_renewal = models.BooleanField(_("Auto Renewal"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

    def __str__(self):
        return f"{self.company.name} - {self.plan.name} - {self.get_subscription_type_display()}"

class Usage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='usages')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='usages')
    feature = models.CharField(_("Feature"), max_length=100)
    value = models.IntegerField(_("Usage Value"))
    date = models.DateField(_("Usage Date"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Usage")
        verbose_name_plural = _("Usages")
        indexes = [
            models.Index(fields=['company', 'feature', 'date']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.feature} - {self.value}"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('credit_card', _('Credit Card')),
        ('bank_transfer', _('Bank Transfer')),
        ('cash', _('Cash')),
    )

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_("Payment Method"), max_length=20, choices=PAYMENT_METHODS)
    payment_date = models.DateField(_("Payment Date"))
    is_paid = models.BooleanField(_("Is Paid"), default=False)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    def __str__(self):
        return f"{self.subscription.company.name} - {self.amount} {self.get_payment_method_display()}"

class APIKey(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='api_keys')
    key_name = models.CharField(_("API Anahtarı Adı"), max_length=100)
    api_key = models.CharField(_("API Anahtarı"), max_length=64, unique=True)
    is_active = models.BooleanField(_("Aktif mi?"), default=True)
    expires_at = models.DateTimeField(_("Son Kullanma Tarihi"), null=True, blank=True)
    last_used_at = models.DateTimeField(_("Son Kullanım Tarihi"), null=True, blank=True)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)

    class Meta:
        verbose_name = _("API Anahtarı")
        verbose_name_plural = _("API Anahtarları")

    def __str__(self):
        return f"{self.company.name} - {self.key_name}"

class APIUsage(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='usages')
    endpoint = models.CharField(_("Endpoint"), max_length=255)
    method = models.CharField(_("HTTP Metodu"), max_length=10)
    status_code = models.IntegerField(_("Durum Kodu"))
    response_time = models.FloatField(_("Yanıt Süresi (ms)"))
    request_data = models.JSONField(_("İstek Verisi"), null=True, blank=True)
    ip_address = models.GenericIPAddressField(_("IP Adresi"))
    user_agent = models.TextField(_("Kullanıcı Ajanı"))
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)

    class Meta:
        verbose_name = _("API Kullanımı")
        verbose_name_plural = _("API Kullanımları")
        indexes = [
            models.Index(fields=['api_key', 'created_at']),
            models.Index(fields=['endpoint', 'method']),
        ]

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('system', _('Sistem Bildirimi')),
        ('payment', _('Ödeme Bildirimi')),
        ('usage', _('Kullanım Bildirimi')),
        ('security', _('Güvenlik Bildirimi')),
    )

    PRIORITY_LEVELS = (
        ('low', _('Düşük')),
        ('medium', _('Orta')),
        ('high', _('Yüksek')),
        ('critical', _('Kritik')),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(_("Bildirim Tipi"), max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(_("Başlık"), max_length=255)
    message = models.TextField(_("Mesaj"))
    priority = models.CharField(_("Öncelik"), max_length=10, choices=PRIORITY_LEVELS, default='medium')
    is_read = models.BooleanField(_("Okundu mu?"), default=False)
    read_at = models.DateTimeField(_("Okunma Tarihi"), null=True, blank=True)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)

    class Meta:
        verbose_name = _("Bildirim")
        verbose_name_plural = _("Bildirimler")
        indexes = [
            models.Index(fields=['company', 'is_read', 'created_at']),
        ]

class AuditLog(models.Model):
    ACTION_TYPES = (
        ('create', _('Oluşturma')),
        ('update', _('Güncelleme')),
        ('delete', _('Silme')),
        ('login', _('Giriş')),
        ('logout', _('Çıkış')),
        ('api_access', _('API Erişimi')),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(_("İşlem"), max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(_("Model Adı"), max_length=100)
    object_id = models.CharField(_("Nesne ID"), max_length=36)
    object_repr = models.CharField(_("Nesne Gösterimi"), max_length=255)
    changes = models.JSONField(_("Değişiklikler"), null=True, blank=True)
    ip_address = models.GenericIPAddressField(_("IP Adresi"))
    user_agent = models.TextField(_("Kullanıcı Ajanı"))
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)

    class Meta:
        verbose_name = _("Denetim Günlüğü")
        verbose_name_plural = _("Denetim Günlükleri")
        indexes = [
            models.Index(fields=['company', 'action', 'created_at']),
            models.Index(fields=['model_name', 'object_id']),
        ]

class Integration(models.Model):
    INTEGRATION_TYPES = (
        ('payment', _('Ödeme Sistemi')),
        ('crm', _('CRM')),
        ('analytics', _('Analitik')),
        ('communication', _('İletişim')),
        ('storage', _('Depolama')),
    )

    STATUS_CHOICES = (
        ('active', _('Aktif')),
        ('pending', _('Beklemede')),
        ('failed', _('Başarısız')),
        ('disabled', _('Devre Dışı')),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='integrations')
    name = models.CharField(_("Entegrasyon Adı"), max_length=100)
    integration_type = models.CharField(_("Entegrasyon Tipi"), max_length=20, choices=INTEGRATION_TYPES)
    provider = models.CharField(_("Sağlayıcı"), max_length=100)
    config = models.JSONField(_("Yapılandırma"), default=dict)
    status = models.CharField(_("Durum"), max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(_("Hata Mesajı"), null=True, blank=True)
    last_sync_at = models.DateTimeField(_("Son Senkronizasyon"), null=True, blank=True)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)

    class Meta:
        verbose_name = _("Entegrasyon")
        verbose_name_plural = _("Entegrasyonlar")
        unique_together = ('company', 'integration_type', 'provider')

    def __str__(self):
        return f"{self.company.name} - {self.get_integration_type_display()} - {self.provider}"