from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TeacherProfileViewSet, StudentProfileViewSet, ParentProfileViewSet, AdminProfileViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'teachers', TeacherProfileViewSet)
router.register(r'students', StudentProfileViewSet)
router.register(r'parents', ParentProfileViewSet)
router.register(r'admins', AdminProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]