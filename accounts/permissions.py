from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOnboardingStudentOrAdmin(BasePermission):
    """
    Allows only:
    - Admins (full access)
    - Students who are not yet onboarded (can only update their own profile)
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin has full access
        if user.role == "admin":
            return True

        # Student can only access their own profile and only if not onboarded
        if user.role == "student" and hasattr(obj, 'user') and obj.user == user:
            return not obj.is_onboarded

        return False

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
    
class IsOwnerOrAdmin(BasePermission):
    """
    Allow only the student (owner) to edit their profile during onboarding.
    Admins can edit any profile at any time.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admins can always edit
        if user.role == "admin":
            return True

        # Only the owner (student) can edit, and only if onboarding is not complete
        if hasattr(obj, "user") and obj.user == user:
            return not obj.completed_onboarding  # Block access if onboarding is complete

        return False
    
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



