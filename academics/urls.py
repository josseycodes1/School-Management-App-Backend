from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassesViewSet, SubjectViewSet, LessonViewSet

router = DefaultRouter()
router.register(r'classes', ClassesViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    path('', include(router.urls)),
]