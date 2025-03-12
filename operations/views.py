from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from .models import (
    Operation, OperationCustomer, OperationSalesPrice,
    OperationDay, OperationItem, OperationSubItem
)
from .serializers import (
    OperationListSerializer, OperationDetailSerializer,
    OperationCustomerSerializer, OperationSalesPriceSerializer,
    OperationDaySerializer, OperationItemSerializer,
    OperationSubItemSerializer
)

class BaseOperationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        elif user.is_company_admin:
            return self.queryset.filter(company=user.company)
        elif user.is_branch_admin:
            return self.queryset.filter(branch=user.branch)
        return self.queryset.filter(follow_by=user)

class OperationViewSet(BaseOperationViewSet):
    queryset = Operation.objects.all()
    filterset_fields = ['status', 'is_active', 'branch', 'buyer_company']
    search_fields = ['reference_number', 'buyer_company__name']

    def get_serializer_class(self):
        if self.action == 'list':
            return OperationListSerializer
        return OperationDetailSerializer

    @swagger_auto_schema(
        operation_summary="Operasyon Durumunu Güncelle",
        operation_description="Operasyonun durumunu günceller.",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Yeni durum (DRAFT, CONFIRMED, COMPLETED, CANCELLED)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: OperationDetailSerializer,
            400: "Geçersiz durum",
            404: "Operasyon bulunamadı"
        }
    )
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        operation = self.get_object()
        new_status = request.query_params.get('status')
        
        if new_status not in [Operation.DRAFT, Operation.CONFIRMED, Operation.COMPLETED, Operation.CANCELLED]:
            return Response({"detail": "Geçersiz durum."}, status=400)
        
        operation.status = new_status
        operation.save()
        serializer = OperationDetailSerializer(operation)
        return Response(serializer.data)

class OperationCustomerViewSet(BaseOperationViewSet):
    queryset = OperationCustomer.objects.all()
    serializer_class = OperationCustomerSerializer
    filterset_fields = ['operation', 'customer_type', 'is_active', 'is_buyer']
    search_fields = ['first_name', 'last_name', 'passport_no']

class OperationSalesPriceViewSet(BaseOperationViewSet):
    queryset = OperationSalesPrice.objects.all()
    serializer_class = OperationSalesPriceSerializer
    filterset_fields = ['operation', 'currency', 'is_active']

class OperationDayViewSet(BaseOperationViewSet):
    queryset = OperationDay.objects.all()
    serializer_class = OperationDaySerializer
    filterset_fields = ['operation', 'is_active']

class OperationItemViewSet(BaseOperationViewSet):
    queryset = OperationItem.objects.all()
    serializer_class = OperationItemSerializer
    filterset_fields = ['operation_day', 'item_type', 'is_active']

    @swagger_auto_schema(
        operation_summary="Maliyet Hesapla",
        operation_description="Operasyon öğesinin maliyetini hesaplar.",
        responses={
            200: openapi.Response(
                description="Başarılı",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'cost_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'cost_currency': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: "Öğe bulunamadı"
        }
    )
    @action(detail=True, methods=['get'])
    def calculate_cost(self, request, pk=None):
        item = self.get_object()
        # Maliyet hesaplama mantığı burada implement edilecek
        return Response({
            "cost_price": item.cost_price,
            "cost_currency": item.cost_currency.code if item.cost_currency else None
        })

class OperationSubItemViewSet(BaseOperationViewSet):
    queryset = OperationSubItem.objects.all()
    serializer_class = OperationSubItemSerializer
    filterset_fields = ['operation_item', 'subitem_type', 'is_active']

    @swagger_auto_schema(
        operation_summary="Maliyet Hesapla",
        operation_description="Alt öğenin maliyetini hesaplar.",
        responses={
            200: openapi.Response(
                description="Başarılı",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'cost_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'cost_currency': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: "Alt öğe bulunamadı"
        }
    )
    @action(detail=True, methods=['get'])
    def calculate_cost(self, request, pk=None):
        subitem = self.get_object()
        # Maliyet hesaplama mantığı burada implement edilecek
        return Response({
            "cost_price": subitem.cost_price,
            "cost_currency": subitem.cost_currency.code if subitem.cost_currency else None
        })
