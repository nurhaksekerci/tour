from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role',
                   'company', 'branch', 'is_company_admin', 'is_branch_admin',
                   'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'role', 'gender',
                  'is_company_admin', 'is_branch_admin', 'company', 'branch')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Kişisel Bilgiler'), {'fields': (
            'first_name', 'last_name', 'email', 'phone', 'gender', 'photo'
        )}),
        (_('Şirket Bilgileri'), {'fields': (
            'company', 'branch', 'role',
            'is_company_admin', 'is_branch_admin'
        )}),
        (_('İzinler'), {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        )}),
        (_('Önemli Tarihler'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'phone', 'gender',
                'company', 'branch', 'role',
                'is_company_admin', 'is_branch_admin',
                'is_active', 'is_staff'
            ),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.is_company_admin:
            return qs.filter(company=request.user.company)
        elif request.user.is_branch_admin:
            return qs.filter(branch=request.user.branch)
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "company":
                kwargs["queryset"] = request.user.company
            elif db_field.name == "branch":
                kwargs["queryset"] = request.user.company.branches.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
