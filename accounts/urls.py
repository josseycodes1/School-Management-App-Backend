# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TeacherProfileViewSet, StudentProfileViewSet, ParentProfileViewSet, AdminProfileViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LoginAPIView 

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'teachers', TeacherProfileViewSet, basename='teacher')
router.register(r'students', StudentProfileViewSet, basename='student')
router.register(r'parents', ParentProfileViewSet, basename='parent')
router.register(r'admins', AdminProfileViewSet, basename='admin')

urlpatterns = [
    path('', include(router.urls)),  # This will prefix all routes with api/accounts/
    path('api/', include(router.urls)),  # Now all routes will be under /api/users/
    path('login/', LoginAPIView.as_view(), name='login'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
