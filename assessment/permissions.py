
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.is_superuser or
            getattr(request.user, 'role', None) == 'admin'
        )