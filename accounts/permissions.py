
from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    """
    Allows access only to authenticated teachers.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'teacher_profile')

class IsStudent(permissions.BasePermission):
    """
    Allows access only to authenticated students.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'student_profile')

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Allows read access to anyone, but write access only to teachers.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(request.user, 'teacher_profile')