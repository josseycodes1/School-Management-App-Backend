from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet
from .views import weekly_attendance_summary

router = DefaultRouter()
router.register(r'records', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
    path('weekly-summary/', weekly_attendance_summary, name='weekly_attendance_summary'),
]