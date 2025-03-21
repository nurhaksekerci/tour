"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger ve OpenAPI şeması için ayar
schema_view = get_schema_view(
    openapi.Info(
        title="Tour SaaS API",
        default_version='v1',
        description="""
        Tour SaaS sistemi için API dokümantasyonu.

        ## Kimlik Doğrulama
        API, JWT (JSON Web Token) tabanlı kimlik doğrulama kullanmaktadır.
        Token almak için `/api/accounts/login/` endpoint'ini kullanın.

        ## Yetkilendirme
        Sistem rol tabanlı yetkilendirme kullanmaktadır:
        - Sistem Yöneticisi
        - Şirket Yöneticisi
        - Şube Yöneticisi
        - Çalışan

        ## Önemli Endpoint'ler
        - `/api/accounts/`: Kullanıcı yönetimi
        - `/api/companies/`: Şirket ve şube yönetimi
        - `/api/companies/plans/`: Abonelik planları
        - `/api/companies/subscriptions/`: Abonelik işlemleri
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin ve API URL'leri
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/companies/', include('companies.urls')),
    path('api/records/', include('records.urls')),
    path('api/operations/', include('operations.urls')),

    # Swagger ve ReDoc URL'leri
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # JSON formatında API şeması
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # ReDoc UI
]

# Statik dosyalar ve medya dosyaları için ayarlamalar
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
