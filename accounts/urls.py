from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, 
    TeacherProfileViewSet, 
    StudentProfileViewSet, 
    ParentProfileViewSet, 
    AdminProfileViewSet,
    LoginAPIView,
    PasswordResetView,
    PasswordResetVerifyView,
    PasswordResetResendView,
    ResendVerificationView,
    StudentOnboardingView,
    StudentOnboardingProgressView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'teachers', TeacherProfileViewSet, basename='teacher')
router.register(r'students', StudentProfileViewSet, basename='student')
router.register(r'parents', ParentProfileViewSet, basename='parent')
router.register(r'admins', AdminProfileViewSet, basename='admin')

urlpatterns = [
    #Custom endpoints FIRST
    path('students/onboarding/', StudentOnboardingView.as_view(), name='student-onboarding'),
    path('students/onboarding/progress/', StudentOnboardingProgressView.as_view(), name='student-onboarding-progress'),


    # Router URLs after
    path('', include(router.urls)),

    # Authentication
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password Reset
    path('password_reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password_reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('password_reset/resend/', PasswordResetResendView.as_view(), name='password-reset-resend'),
    path('users/resend_verification/', ResendVerificationView.as_view(), name='resend-verification'),
]
