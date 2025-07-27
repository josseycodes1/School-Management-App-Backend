from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "admin"

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "teacher"

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "student"

class IsParent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "parent"

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            # Everyone who is logged in can see (GET, HEAD, OPTIONS)
            return request.user and request.user.is_authenticated
        # Only admin can edit, create, delete
        return request.user and request.user.is_authenticated and request.user.role == "admin"
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            # Everyone who is logged in can see (GET, HEAD, OPTIONS)
            return request.user and request.user.is_authenticated
        # Only admin can edit, create, delete
        return request.user and request.user.is_authenticated and request.user.role == "admin"

