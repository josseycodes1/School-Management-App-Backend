from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    - Anyone authenticated can read (GET, HEAD, OPTIONS).
    - Only admins can write (POST, PATCH, PUT, DELETE).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == "admin"


class IsStudentOnboarding(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admins can always edit
        if user.role == "admin":
            return True

        # Students can only edit their own profile before completing onboarding
        if user.role == "student" and hasattr(obj, "user") and obj.user == user:
            return not obj.is_onboarded

        # Teachers, Parents, and others → read-only
        return request.method in SAFE_METHODS


class RolePermission(BasePermission):
    def has_permission(self, request, view):
        required_roles = getattr(view, "required_roles", None)

        if not required_roles:
            return False

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in required_roles
        )
