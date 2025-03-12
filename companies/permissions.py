from rest_framework import permissions

class IsCompanyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_company_admin
        )

class IsBranchAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.is_company_admin or 
            request.user.is_branch_admin
        )

class IsCompanyMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.company is not None

class CanManageCompany(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        if request.method in permissions.SAFE_METHODS:
            return request.user.company == obj
            
        return request.user.is_company_admin and request.user.company == obj

class CanManageBranch(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        if request.method in permissions.SAFE_METHODS:
            return request.user.company == obj.company
            
        if request.user.is_company_admin:
            return request.user.company == obj.company
            
        return request.user.is_branch_admin and request.user.branch == obj 