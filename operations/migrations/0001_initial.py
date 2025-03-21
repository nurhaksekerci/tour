# Generated by Django 5.1.7 on 2025-03-12 14:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0002_currency_alter_branch_options_and_more'),
        ('records', '0002_alter_museum_city_alter_transfer_end_city_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_number', models.CharField(blank=True, max_length=50, unique=True, verbose_name='Reference Number')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(verbose_name='End Date')),
                ('status', models.CharField(choices=[('DRAFT', 'Taslak'), ('CONFIRMED', 'Onaylandı'), ('COMPLETED', 'Tamamlandı'), ('CANCELLED', 'İptal Edildi')], default='DRAFT', max_length=20, verbose_name='Status')),
                ('total_pax', models.PositiveIntegerField(default=0, verbose_name='Total Pax')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.branch', verbose_name='Branch')),
                ('buyer_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='records.buyercompany', verbose_name='Buyer Company')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company', verbose_name='Company')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_operations', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('follow_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='following_operations', to=settings.AUTH_USER_MODEL, verbose_name='Follow By')),
            ],
            options={
                'verbose_name': 'Operation',
                'verbose_name_plural': 'Operations',
                'ordering': ['-start_date', 'reference_number'],
            },
        ),
        migrations.CreateModel(
            name='OperationCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last Name')),
                ('customer_type', models.CharField(choices=[('ADULT', 'Yetişkin'), ('CHILD', 'Çocuk'), ('INFANT', 'Bebek')], max_length=20, verbose_name='Customer Type')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Birth Date')),
                ('passport_no', models.CharField(blank=True, max_length=50, null=True, verbose_name='Passport No')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('is_buyer', models.BooleanField(default=False, verbose_name='Is Buyer')),
                ('contact_info', models.CharField(blank=True, help_text='Phone number or email', max_length=100, null=True, verbose_name='Contact Info')),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customers', to='operations.operation', verbose_name='Operation')),
            ],
            options={
                'verbose_name': 'Operation Customer',
                'verbose_name_plural': 'Operation Customers',
            },
        ),
        migrations.CreateModel(
            name='OperationDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Date')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='operations.operation', verbose_name='Operation')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='OperationItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(choices=[('VEHICLE', 'Araçlı'), ('NO_VEHICLE_TOUR', 'Araçsız Tur'), ('NO_VEHICLE_ACTIVITY', 'Araçsız Aktivite')], max_length=20, verbose_name='Item Type')),
                ('pick_time', models.TimeField(blank=True, null=True, verbose_name='Pick Time')),
                ('pick_up_location', models.CharField(blank=True, max_length=100, null=True, verbose_name='Pick Up Location')),
                ('drop_off_location', models.CharField(blank=True, max_length=100, null=True, verbose_name='Drop Off Location')),
                ('driver_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Driver Name')),
                ('driver_phone', models.CharField(blank=True, max_length=100, null=True, verbose_name='Driver Phone')),
                ('vehicle_plate_no', models.CharField(blank=True, max_length=100, null=True, verbose_name='Vehicle Plate No')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('sales_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Sales Price')),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost Price')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('activity_cost', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='records.activitycost', verbose_name='Activity Cost')),
                ('activity_supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.activitysupplier', verbose_name='Activity Supplier')),
                ('cost_currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='item_cost_currency', to='companies.currency', verbose_name='Cost Currency')),
                ('no_vehicle_activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.activity', verbose_name='No Vehicle Activity')),
                ('no_vehicle_tour', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.novehicletour', verbose_name='No Vehicle Tour')),
                ('operation_day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='operations.operationday', verbose_name='Operation Day')),
                ('sales_currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='item_sales_currency', to='companies.currency', verbose_name='Sales Currency')),
                ('vehicle_cost', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='records.vehiclecost', verbose_name='Vehicle Cost')),
                ('vehicle_supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.vehiclesupplier', verbose_name='Vehicle Supplier')),
                ('vehicle_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.vehicletype', verbose_name='Vehicle Type')),
            ],
            options={
                'verbose_name': 'Operation Item',
                'verbose_name_plural': 'Operation Items',
                'ordering': ['pick_time'],
            },
        ),
        migrations.CreateModel(
            name='OperationSalesPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='companies.currency', verbose_name='Currency')),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_prices', to='operations.operation', verbose_name='Operation')),
            ],
        ),
        migrations.CreateModel(
            name='OperationSubItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.PositiveIntegerField(verbose_name='Ordering')),
                ('subitem_type', models.CharField(choices=[('TOUR', 'Tur'), ('TRANSFER', 'Transfer'), ('ACTIVITY', 'Aktivite'), ('MUSEUM', 'Müze'), ('HOTEL', 'Otel'), ('GUIDE', 'Rehber'), ('OTHER_PRICE', 'Diğer Ücret')], max_length=20, verbose_name='Subitem Type')),
                ('room_type', models.CharField(blank=True, choices=[('SINGLE', 'Tek Kişilik'), ('DOUBLE', 'Çift Kişilik'), ('TRIPLE', 'Aile')], max_length=20, null=True, verbose_name='Room Type')),
                ('is_guide', models.BooleanField(default=False, verbose_name='Is Guide')),
                ('other_price_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Other Price Description')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('sales_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Sales Price')),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost Price')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.activity', verbose_name='Activity')),
                ('activity_cost', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='records.activitycost', verbose_name='Activity Cost')),
                ('activity_supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.activitysupplier', verbose_name='Activity Supplier')),
                ('cost_currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subitem_cost_currency', to='companies.currency', verbose_name='Cost Currency')),
                ('guide', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.guide', verbose_name='Guide')),
                ('hotel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.hotel', verbose_name='Hotel')),
                ('museums', models.ManyToManyField(blank=True, null=True, related_name='museums', to='records.museum', verbose_name='Museums')),
                ('operation_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subitems', to='operations.operationitem', verbose_name='Operation Item')),
                ('sales_currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subitem_sales_currency', to='companies.currency', verbose_name='Sales Currency')),
                ('tour', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.tour', verbose_name='Tour')),
                ('transfer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='records.transfer', verbose_name='Transfer')),
            ],
            options={
                'ordering': ['ordering'],
            },
        ),
    ]
