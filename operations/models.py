from django.db import models
from django.core.exceptions import ValidationError
from companies.models import Company, Currency, Branch
from records.models import (
    BuyerCompany, Tour, Transfer, Activity, Museum, Hotel, Guide,
    VehicleSupplier, NoVehicleTour, VehicleType, VehicleCost, ActivitySupplier, ActivityCost
)
from accounts.models import CustomUser
from datetime import timedelta
class Operation(models.Model):
    DRAFT = 'DRAFT'
    CONFIRMED = 'CONFIRMED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (DRAFT, 'Taslak'),
        (CONFIRMED, 'Onaylandı'),
        (COMPLETED, 'Tamamlandı'),
        (CANCELLED, 'İptal Edildi'),
    ]

    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, verbose_name="Branch", on_delete=models.CASCADE)
    buyer_company = models.ForeignKey(BuyerCompany, verbose_name="Buyer Company", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        CustomUser,
        verbose_name="Created By",
        on_delete=models.PROTECT,
        related_name='created_operations'
    )
    follow_by = models.ForeignKey(
        CustomUser,
        verbose_name="Follow By",
        on_delete=models.PROTECT,
        related_name='following_operations'
    )
    reference_number = models.CharField(
        verbose_name="Reference Number",
        max_length=50,
        unique=True,
        blank=True
    )
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    status = models.CharField(
        verbose_name="Status",
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT
    )
    total_pax = models.PositiveIntegerField(verbose_name="Total Pax", default=0)
    notes = models.TextField(verbose_name="Notes", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_start_date = None
        old_end_date = None

        # Referans numarası oluşturma
        if not self.reference_number:
            if not self.pk or self.buyer_company.short_name != Operation.objects.get(pk=self.pk).buyer_company.short_name or self.start_date != Operation.objects.get(pk=self.pk).start_date:
                kisa_ad = self.buyer_company.short_name
                tarih_format = self.start_date.strftime("%d%m%y")

                # Benzersiz bir referans numarası oluşturana kadar döngü
                tur_sayisi = 1
                while True:
                    potansiyel_referans = f"{kisa_ad}{tarih_format}{str(tur_sayisi).zfill(3)}"
                    if not Operation.objects.filter(reference_number=potansiyel_referans).exclude(pk=self.pk).exists():
                        self.reference_number = potansiyel_referans
                        break
                    tur_sayisi += 1

        # Gün oluşturma işlemleri
        if not is_new:
            old_instance = Operation.objects.get(pk=self.pk)
            old_start_date = old_instance.start_date
            old_end_date = old_instance.end_date

        super().save(*args, **kwargs)

        # Yeni kayıt veya tarihler değişmişse günleri oluştur
        if is_new or old_start_date != self.start_date or old_end_date != self.end_date:
            if not is_new:
                self.days.all().delete()

            current_date = self.start_date
            while current_date <= self.end_date:
                OperationDay.objects.create(
                    operation=self,
                    date=current_date,
                    is_active=True
                )
                current_date += timedelta(days=1)

    def __str__(self):
        return f"{self.reference_number} - {self.buyer_company.name} (Follow by: {self.follow_by.get_full_name()})"

    class Meta:
        verbose_name = "Operation"
        verbose_name_plural = "Operations"
        ordering = ['-start_date', 'reference_number']

class OperationCustomer(models.Model):
    ADULT = 'ADULT'
    CHILD = 'CHILD'
    INFANT = 'INFANT'

    CUSTOMER_TYPE_CHOICES = [
        (ADULT, 'Yetişkin'),
        (CHILD, 'Çocuk'),
        (INFANT, 'Bebek'),
    ]

    operation = models.ForeignKey(Operation, verbose_name="Operation", on_delete=models.CASCADE, related_name='customers')
    first_name = models.CharField(verbose_name="First Name", max_length=100)
    last_name = models.CharField(verbose_name="Last Name", max_length=100)
    customer_type = models.CharField(verbose_name="Customer Type", max_length=20, choices=CUSTOMER_TYPE_CHOICES)
    birth_date = models.DateField(verbose_name="Birth Date", null=True, blank=True)
    passport_no = models.CharField(verbose_name="Passport No", max_length=50, null=True, blank=True)
    notes = models.TextField(verbose_name="Notes", null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)
    is_buyer = models.BooleanField(verbose_name="Is Buyer", default=False)
    contact_info = models.CharField(verbose_name="Contact Info", max_length=100, null=True, blank=True,
                                  help_text="Phone number or email")

    def clean(self):
        if self.pk:  # Sadece kayıtlı müşteriler için kontrol yap
            if not self.is_buyer and not self.operation.customers.filter(is_buyer=True).exists():
                raise ValidationError("En az bir müşteri satın alan olarak işaretlenmelidir.")

        # Satın alan kişinin iletişim bilgisi zorunlu
        if self.is_buyer and not self.contact_info:
            raise ValidationError("Contact info is required for buyer")

    def get_full_name(self):
        """Müşterinin tam adını döndürür"""
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Müşteri eklendiğinde veya silindiğinde total_pax'i güncelle
        if is_new or not self.is_active:
            active_customers = OperationCustomer.objects.filter(
                operation=self.operation,
                is_active=True
            ).count()

            self.operation.total_pax = active_customers
            self.operation.save(update_fields=['total_pax'])

    def delete(self, *args, **kwargs):
        operation = self.operation
        super().delete(*args, **kwargs)

        # Müşteri silindiğinde total_pax'i güncelle
        active_customers = OperationCustomer.objects.filter(
            operation=operation,
            is_active=True
        ).count()

        operation.total_pax = active_customers
        operation.save(update_fields=['total_pax'])

    class Meta:
        verbose_name = "Operation Customer"
        verbose_name_plural = "Operation Customers"

class OperationSalesPrice(models.Model):
    operation = models.ForeignKey(Operation, verbose_name="Operation", on_delete=models.CASCADE, related_name='sales_prices')
    price = models.DecimalField(verbose_name="Price", max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, verbose_name="Currency", on_delete=models.PROTECT)
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return f"{self.operation.reference_number} - {self.price} {self.currency} Price"

class OperationDay(models.Model):
    operation = models.ForeignKey(Operation, verbose_name="Operation", on_delete=models.CASCADE, related_name='days')
    date = models.DateField(verbose_name="Date")
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return f"{self.operation} - {self.date}"

    class Meta:
        ordering = ['date']

class OperationItem(models.Model):
    VEHICLE = 'VEHICLE'
    NO_VEHICLE_TOUR = 'NO_VEHICLE_TOUR'
    NO_VEHICLE_ACTIVITY = 'NO_VEHICLE_ACTIVITY'

    ITEM_TYPE_CHOICES = [
        (VEHICLE, 'Araçlı'),
        (NO_VEHICLE_TOUR, 'Araçsız Tur'),
        (NO_VEHICLE_ACTIVITY, 'Araçsız Aktivite'),
    ]

    operation_day = models.ForeignKey(OperationDay, verbose_name="Operation Day", on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(verbose_name="Item Type", max_length=20, choices=ITEM_TYPE_CHOICES)
    
    #ortak alanlar 1
    pick_time = models.TimeField(verbose_name="Pick Time", null=True, blank=True)
    pick_up_location = models.CharField(verbose_name="Pick Up Location", max_length=100, null=True, blank=True)
    drop_off_location = models.CharField(verbose_name="Drop Off Location", max_length=100, null=True, blank=True)
    
    #Seçim araç ise
    vehicle_type = models.ForeignKey(VehicleType, verbose_name="Vehicle Type", on_delete=models.PROTECT, null=True, blank=True)
    vehicle_supplier = models.ForeignKey(VehicleSupplier, verbose_name="Vehicle Supplier", on_delete=models.PROTECT, null=True, blank=True)
    vehicle_cost = models.ForeignKey(VehicleCost, verbose_name="Vehicle Cost", on_delete=models.CASCADE, null=True, blank=True)
    driver_name = models.CharField(verbose_name="Driver Name", max_length=100, null=True, blank=True)
    driver_phone = models.CharField(verbose_name="Driver Phone", max_length=100, null=True, blank=True)
    vehicle_plate_no = models.CharField(verbose_name="Vehicle Plate No", max_length=100, null=True, blank=True)

    #Seçim araçsız tur ise
    no_vehicle_tour = models.ForeignKey(NoVehicleTour, verbose_name="No Vehicle Tour", on_delete=models.PROTECT, null=True, blank=True)

    #seçim araçsız aktivite ise
    no_vehicle_activity = models.ForeignKey(Activity, verbose_name="No Vehicle Activity", on_delete=models.PROTECT, null=True, blank=True)
    activity_supplier = models.ForeignKey(ActivitySupplier, verbose_name="Activity Supplier", on_delete=models.PROTECT, null=True, blank=True)
    activity_cost = models.ForeignKey(ActivityCost, verbose_name="Activity Cost", on_delete=models.CASCADE, null=True, blank=True)

    #ortak alanlar 2
    notes = models.TextField(verbose_name="Notes", null=True, blank=True)
    sales_price = models.DecimalField(verbose_name="Sales Price", max_digits=10, decimal_places=2, blank=True, null=True)
    sales_currency = models.ForeignKey(Currency, verbose_name="Sales Currency", related_name='item_sales_currency', on_delete=models.PROTECT, null=True, blank=True)
    cost_price = models.DecimalField(verbose_name="Cost Price", max_digits=10, decimal_places=2, blank=True, null=True)
    cost_currency = models.ForeignKey(Currency, verbose_name="Cost Currency", related_name='item_cost_currency', on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def clean(self):
        if self.item_type == self.VEHICLE and not self.vehicle_type:
            raise ValidationError("Vehicle supplier is required for vehicle items")
        elif self.item_type == self.NO_VEHICLE_TOUR and not self.no_vehicle_tour:
            raise ValidationError("No vehicle tour is required for no vehicle tour items")
        elif self.item_type == self.NO_VEHICLE_ACTIVITY and not self.no_vehicle_activity:
            raise ValidationError("No vehicle activity is required for no vehicle activity items")

    def __str__(self):
        return f"{self.operation_day} - {self.get_item_type_display()}"

    class Meta:
        verbose_name = "Operation Item"
        verbose_name_plural = "Operation Items"
        ordering = ['pick_time']

class OperationSubItem(models.Model):
    TOUR = 'TOUR'
    TRANSFER = 'TRANSFER'
    ACTIVITY = 'ACTIVITY'
    MUSEUM = 'MUSEUM'
    HOTEL = 'HOTEL'
    GUIDE = 'GUIDE'
    OTHER_PRICE = 'OTHER_PRICE'

    ROOM_TYPE_CHOICES = [
        ('SINGLE', 'Tek Kişilik'),
        ('DOUBLE', 'Çift Kişilik'),
        ('TRIPLE', 'Aile'),
    ]
    SUBITEM_TYPE_CHOICES = [
        (TOUR, 'Tur'),
        (TRANSFER, 'Transfer'),
        (ACTIVITY, 'Aktivite'),
        (MUSEUM, 'Müze'),
        (HOTEL, 'Otel'),
        (GUIDE, 'Rehber'),
        (OTHER_PRICE, 'Diğer Ücret'),
    ]

    operation_item = models.ForeignKey(OperationItem, verbose_name="Operation Item", on_delete=models.CASCADE, related_name='subitems')
    ordering = models.PositiveIntegerField(verbose_name="Ordering")
    subitem_type = models.CharField(verbose_name="Subitem Type", max_length=20, choices=SUBITEM_TYPE_CHOICES)

    tour = models.ForeignKey(Tour, verbose_name="Tour", on_delete=models.PROTECT, null=True, blank=True)

    transfer = models.ForeignKey(Transfer, verbose_name="Transfer", on_delete=models.PROTECT, null=True, blank=True)

    museums = models.ManyToManyField(Museum, verbose_name="Museums", blank=True, null=True, related_name='museums')

    hotel = models.ForeignKey(Hotel, verbose_name="Hotel", on_delete=models.PROTECT, null=True, blank=True)
    room_type = models.CharField(verbose_name="Room Type", max_length=20, choices=ROOM_TYPE_CHOICES, null=True, blank=True)

    is_guide = models.BooleanField(verbose_name="Is Guide", default=False)
    guide = models.ForeignKey(Guide, verbose_name="Guide", on_delete=models.PROTECT, null=True, blank=True)

    activity = models.ForeignKey(Activity, verbose_name="Activity", on_delete=models.PROTECT, null=True, blank=True)
    activity_supplier = models.ForeignKey(ActivitySupplier, verbose_name="Activity Supplier", on_delete=models.PROTECT, null=True, blank=True)
    activity_cost = models.ForeignKey(ActivityCost, verbose_name="Activity Cost", on_delete=models.CASCADE, null=True, blank=True)

    other_price_description = models.CharField(verbose_name="Other Price Description", max_length=255, null=True, blank=True)

    notes = models.TextField(verbose_name="Notes", null=True, blank=True)
    sales_price = models.DecimalField(verbose_name="Sales Price", max_digits=10, decimal_places=2, blank=True, null=True)
    sales_currency = models.ForeignKey(Currency, verbose_name="Sales Currency", related_name='subitem_sales_currency', on_delete=models.PROTECT, null=True, blank=True)
    cost_price = models.DecimalField(verbose_name="Cost Price", max_digits=10, decimal_places=2, blank=True, null=True)
    cost_currency = models.ForeignKey(Currency, verbose_name="Cost Currency", related_name='subitem_cost_currency', on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def clean(self):
        # Item tipine göre subitem validasyonları
        parent_type = self.operation_item.item_type

        if parent_type == OperationItem.VEHICLE:
            if self.subitem_type not in [self.TOUR, self.TRANSFER, self.ACTIVITY, self.MUSEUM, self.HOTEL, self.GUIDE, self.OTHER_PRICE]:
                raise ValidationError("Invalid subitem type for vehicle item")
        elif parent_type == OperationItem.NO_VEHICLE_TOUR:
            if self.subitem_type not in [self.MUSEUM, self.ACTIVITY, self.HOTEL, self.GUIDE, self.OTHER_PRICE]:
                raise ValidationError("Invalid subitem type for no vehicle tour")
        elif parent_type == OperationItem.NO_VEHICLE_ACTIVITY:
            if self.subitem_type not in [self.ACTIVITY, self.GUIDE, self.OTHER_PRICE]:
                raise ValidationError("Invalid subitem type for no vehicle activity")

    def __str__(self):
        return f"{self.operation_item} - {self.get_subitem_type_display()}"

    class Meta:
        ordering = ['ordering']