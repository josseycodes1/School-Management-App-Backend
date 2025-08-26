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
    StudentOnboardingView,
    StudentOnboardingProgressView,
    TeacherOnboardingView,
    TeacherOnboardingProgressView,
    ParentOnboardingView,
    ParentOnboardingProgressView,
    ClassesViewSet,
    SubjectViewSet
    
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'teachers', TeacherProfileViewSet, basename='teacher')
router.register(r'students', StudentProfileViewSet, basename='student')
router.register(r'parents', ParentProfileViewSet, basename='parent')
router.register(r'admins', AdminProfileViewSet, basename='admin')
router.register(r'classes', ClassesViewSet, basename='classes')
router.register(r'subjects', SubjectViewSet, basename='subject')
# GET /api/accounts/subjects/by_class/?class_id=1
# GET /api/accounts/subjects/my_subjects/


urlpatterns = [
    #Custom endpoints FIRST
    path('user-counts/', views.user_counts, name='user-counts'),
     path('api/accounts/user/<uuid:user_id>/', views.get_user_details, name='user-details'),
    path('students/onboarding/', StudentOnboardingView.as_view(), name='student-onboarding'),
    path('students/onboarding/progress/', StudentOnboardingProgressView.as_view(), name='student-onboarding-progress'),
    path('teachers/onboarding/', TeacherOnboardingView.as_view(), name='teacher-onboarding'),
    path('teachers/onboarding/progress/', TeacherOnboardingProgressView.as_view(), name='teacher-onboarding-progress'),
    path('parents/onboarding/', ParentOnboardingView.as_view(), name='parent-onboarding'),
    path('parents/onboarding/progress/', ParentOnboardingProgressView.as_view(), name='parent-onboarding-progress'),


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
]
