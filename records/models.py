from django.db import models
from companies.models import Company, Currency, City
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

class VehicleType(models.Model):
    name = models.CharField(verbose_name="Vehicle Type", max_length=50)  # Binek, Minivan vs.
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return self.name


class BuyerCompany(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Company Name", max_length=255)
    short_name = models.CharField(verbose_name="Short Name", max_length=50, unique=True)
    contact = models.CharField(verbose_name="Contact", max_length=255)
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return f"{self.name} ({self.short_name})"

    class Meta:
        verbose_name_plural = "Buyer Companies"

class Tour(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Tour Name", max_length=255)
    start_city = models.ForeignKey(City, verbose_name="Start City", on_delete=models.CASCADE, related_name='tour_starts')
    end_city = models.ForeignKey(City, verbose_name="End City", on_delete=models.CASCADE, related_name='tour_ends')
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return f"{self.name} ({self.start_city} - {self.end_city})"

class NoVehicleTour(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Tour Name", max_length=255)
    city = models.ForeignKey(City, verbose_name="City", on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return f"{self.name} ({self.city})"

class Transfer(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Transfer Name", max_length=255)
    start_city = models.ForeignKey(City, verbose_name="Start City", on_delete=models.CASCADE, related_name='transfer_starts')
    end_city = models.ForeignKey(City, verbose_name="End City", on_delete=models.CASCADE, related_name='transfer_ends')
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return f"{self.name} ({self.start_city} - {self.end_city})"

class Hotel(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Hotel Name", max_length=255)
    city = models.ForeignKey(City, verbose_name="City", on_delete=models.CASCADE)
    single_price = models.DecimalField(verbose_name="Single Room Price", max_digits=10, decimal_places=2)
    double_price = models.DecimalField(verbose_name="Double Room Price", max_digits=10, decimal_places=2)
    triple_price = models.DecimalField(verbose_name="Family Room Price", max_digits=10, decimal_places=2)
    currency = models.ForeignKey(
        Currency, 
        verbose_name="Currency", 
        on_delete=models.PROTECT,
        related_name='hotels'
    )
    valid_until = models.DateField(verbose_name="Valid Until")
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return f"{self.name} ({self.city})"

    def clean(self):
        if self.valid_until and self.valid_until < timezone.now().date():
            raise ValidationError("Geçerlilik tarihi geçmiş tarih olamaz")

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            HotelPriceHistory.objects.create(
                hotel=self,
                currency=self.currency,
                valid_from=timezone.now().date(),
                valid_until=self.valid_until,
                single_price=self.single_price,
                double_price=self.double_price,
                triple_price=self.triple_price
            )
        else:
            old_instance = Hotel.objects.get(pk=self.pk)
            if (old_instance.single_price != self.single_price or 
                old_instance.double_price != self.double_price or
                old_instance.triple_price != self.triple_price or
                old_instance.currency != self.currency):
                
                HotelPriceHistory.objects.filter(
                    hotel=self,
                    valid_until__gte=timezone.now().date()
                ).update(valid_until=timezone.now().date())
                
                HotelPriceHistory.objects.create(
                    hotel=self,
                    currency=self.currency,
                    valid_from=timezone.now().date(),
                    valid_until=self.valid_until,
                    single_price=self.single_price,
                    double_price=self.double_price,
                    triple_price=self.triple_price
                )
            
            super().save(*args, **kwargs)

    def get_price_for_date(self, target_date):
        return self.price_history.filter(
            valid_from__lte=target_date,
            valid_until__gte=target_date
        ).first()

class Museum(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Museum Name", max_length=255)
    city = models.ForeignKey(City, verbose_name="City", on_delete=models.CASCADE)
    local_price = models.DecimalField(
        verbose_name="Local Price", 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    foreign_price = models.DecimalField(
        verbose_name="Foreign Price", 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.ForeignKey(Currency, verbose_name="Currency", on_delete=models.PROTECT, related_name='museums')
    valid_until = models.DateField(verbose_name="Valid Until")
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return f"{self.name} ({self.city})"

    def clean(self):
        if self.valid_until and self.valid_until < timezone.now().date():
            raise ValidationError("Geçerlilik tarihi geçmiş tarih olamaz")

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            MuseumPriceHistory.objects.create(
                museum=self,
                currency=self.currency,
                valid_from=timezone.now().date(),
                valid_until=self.valid_until,
                local_price=self.local_price,
                foreign_price=self.foreign_price
            )
        else:
            old_instance = Museum.objects.get(pk=self.pk)
            if (old_instance.local_price != self.local_price or 
                old_instance.foreign_price != self.foreign_price or
                old_instance.currency != self.currency):
                
                MuseumPriceHistory.objects.filter(
                    museum=self,
                    valid_until__gte=timezone.now().date()
                ).update(valid_until=timezone.now().date())
                
                MuseumPriceHistory.objects.create(
                    museum=self,
                    currency=self.currency,
                    valid_from=timezone.now().date(),
                    valid_until=self.valid_until,
                    local_price=self.local_price,
                    foreign_price=self.foreign_price
                )
            
            super().save(*args, **kwargs)

    def get_price_for_date(self, target_date):
        return self.price_history.filter(
            valid_from__lte=target_date,
            valid_until__gte=target_date
        ).first()

class Activity(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Activity Name", max_length=255)
    cities = models.ManyToManyField(City, verbose_name="Cities")
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    def clean(self):
        if self.valid_until and self.valid_until < timezone.now().date():
            raise ValidationError("Geçerlilik tarihi geçmiş tarih olamaz")

class Guide(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Guide Name", max_length=255)
    phone = models.CharField(verbose_name="Phone Number", max_length=20)
    document_no = models.CharField(verbose_name="Document Number", max_length=50)
    cities = models.ManyToManyField(City, verbose_name="Cities")
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return self.name

class VehicleSupplier(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Supplier Name", max_length=255)
    cities = models.ManyToManyField(City, verbose_name="Service Cities")
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return self.name

class ActivitySupplier(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Supplier Name", max_length=255)
    cities = models.ManyToManyField(City, verbose_name="Service Cities")
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return self.name

class VehicleCost(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    supplier = models.ForeignKey(VehicleSupplier, verbose_name="Supplier", on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, verbose_name="Tour", on_delete=models.CASCADE, null=True, blank=True)
    transfer = models.ForeignKey(Transfer, verbose_name="Transfer", on_delete=models.CASCADE, null=True, blank=True)
    car_cost = models.DecimalField(verbose_name="Car Cost", max_digits=10, decimal_places=2)
    minivan_cost = models.DecimalField(verbose_name="Minivan Cost", max_digits=10, decimal_places=2)
    minibus_cost = models.DecimalField(verbose_name="Minibus Cost", max_digits=10, decimal_places=2)
    midibus_cost = models.DecimalField(verbose_name="Midibus Cost", max_digits=10, decimal_places=2)
    bus_cost = models.DecimalField(verbose_name="Bus Cost", max_digits=10, decimal_places=2)
    currency = models.ForeignKey(
        Currency, 
        verbose_name="Currency", 
        on_delete=models.PROTECT,
        related_name='vehicle_costs'
    )
    valid_until = models.DateField(verbose_name="Valid Until")
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.tour and self.transfer:
            raise ValidationError("Cannot select both tour and transfer")
        if not self.tour and not self.transfer:
            raise ValidationError("Must select either tour or transfer")

    def save(self, *args, **kwargs):
        self.clean()
        if not self.pk:
            super().save(*args, **kwargs)
            VehicleCostHistory.objects.create(
                vehicle_cost=self,
                currency=self.currency,
                valid_from=timezone.now().date(),
                valid_until=self.valid_until,
                car_cost=self.car_cost,
                minivan_cost=self.minivan_cost,
                minibus_cost=self.minibus_cost,
                midibus_cost=self.midibus_cost,
                bus_cost=self.bus_cost
            )
        else:
            old_instance = VehicleCost.objects.get(pk=self.pk)
            if (old_instance.car_cost != self.car_cost or 
                old_instance.minivan_cost != self.minivan_cost or
                old_instance.minibus_cost != self.minibus_cost or
                old_instance.midibus_cost != self.midibus_cost or
                old_instance.bus_cost != self.bus_cost or
                old_instance.currency != self.currency):
                
                VehicleCostHistory.objects.filter(
                    vehicle_cost=self,
                    valid_until__gte=timezone.now().date()
                ).update(valid_until=timezone.now().date())
                
                VehicleCostHistory.objects.create(
                    vehicle_cost=self,
                    currency=self.currency,
                    valid_from=timezone.now().date(),
                    valid_until=self.valid_until,
                    car_cost=self.car_cost,
                    minivan_cost=self.minivan_cost,
                    minibus_cost=self.minibus_cost,
                    midibus_cost=self.midibus_cost,
                    bus_cost=self.bus_cost
                )
            
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supplier.name} - {'Tour' if self.tour else 'Transfer'}"

    def get_price_for_date(self, target_date):
        return self.price_history.filter(
            valid_from__lte=target_date,
            valid_until__gte=target_date,
            is_active=True
        ).first()

class ActivityCost(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, verbose_name="Activity", on_delete=models.CASCADE)
    supplier = models.ForeignKey(ActivitySupplier, verbose_name="Supplier", on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name="Price", max_digits=10, decimal_places=2)
    currency = models.ForeignKey(
        Currency, 
        verbose_name="Currency", 
        on_delete=models.PROTECT,
        related_name='activity_costs'
    )
    valid_until = models.DateField(verbose_name="Valid Until")
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)

    def __str__(self):
        return f"{self.activity.name} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            ActivityCostHistory.objects.create(
                activity_cost=self,
                currency=self.currency,
                valid_from=timezone.now().date(),
                valid_until=self.valid_until,
                price=self.price
            )
        else:
            old_instance = ActivityCost.objects.get(pk=self.pk)
            if (old_instance.price != self.price or 
                old_instance.currency != self.currency):
                
                ActivityCostHistory.objects.filter(
                    activity_cost=self,
                    valid_until__gte=timezone.now().date()
                ).update(valid_until=timezone.now().date())
                
                ActivityCostHistory.objects.create(
                    activity_cost=self,
                    currency=self.currency,
                    valid_from=timezone.now().date(),
                    valid_until=self.valid_until,
                    price=self.price
                )
            
            super().save(*args, **kwargs)

    def get_price_for_date(self, target_date):
        return self.price_history.filter(
            valid_from__lte=target_date,
            valid_until__gte=target_date,
            is_active=True
        ).first()

# Fiyat geçmişi için abstract base model
class PriceHistoryBase(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    valid_from = models.DateField(verbose_name="Valid From")
    valid_until = models.DateField(verbose_name="Valid Until")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def clean(self):
        if self.valid_until and self.valid_until < self.valid_from:
            raise ValidationError("Bitiş tarihi başlangıç tarihinden önce olamaz")

# Otel fiyat geçmişi
class HotelPriceHistory(PriceHistoryBase):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='price_history')
    single_price = models.DecimalField(max_digits=10, decimal_places=2)
    double_price = models.DecimalField(max_digits=10, decimal_places=2)
    triple_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.hotel.name} ({self.valid_from} - {self.valid_until})"

    class Meta:
        verbose_name = "Hotel Price History"
        verbose_name_plural = "Hotel Price Histories"
        ordering = ['-valid_from']

# Müze fiyat geçmişi
class MuseumPriceHistory(PriceHistoryBase):
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE, related_name='price_history')
    local_price = models.DecimalField(max_digits=10, decimal_places=2)
    foreign_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.museum.name} ({self.valid_from} - {self.valid_until})"

    class Meta:
        verbose_name = "Museum Price History"
        verbose_name_plural = "Museum Price Histories"
        ordering = ['-valid_from']

# Araç maliyet geçmişi
class VehicleCostHistory(PriceHistoryBase):
    vehicle_cost = models.ForeignKey(VehicleCost, on_delete=models.CASCADE, related_name='price_history')
    car_cost = models.DecimalField(max_digits=10, decimal_places=2)
    minivan_cost = models.DecimalField(max_digits=10, decimal_places=2)
    minibus_cost = models.DecimalField(max_digits=10, decimal_places=2)
    midibus_cost = models.DecimalField(max_digits=10, decimal_places=2)
    bus_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.vehicle_cost.supplier.name} ({self.valid_from} - {self.valid_until})"

    class Meta:
        verbose_name = "Vehicle Cost History"
        verbose_name_plural = "Vehicle Cost Histories"
        ordering = ['-valid_from']

# Aktivite maliyet geçmişi
class ActivityCostHistory(PriceHistoryBase):
    activity_cost = models.ForeignKey(ActivityCost, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.activity_cost.activity.name} ({self.valid_from} - {self.valid_until})"

    class Meta:
        verbose_name = "Activity Cost History"
        verbose_name_plural = "Activity Cost Histories"
        ordering = ['-valid_from']