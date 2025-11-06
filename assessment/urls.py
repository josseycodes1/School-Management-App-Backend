from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GradeViewSet,
    ExamViewSet,
    AssignmentViewSet,
    ResultViewSet
)


router = DefaultRouter()
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'results', ResultViewSet, basename='result')



custom_urlpatterns = [
   
]

urlpatterns = [
    path('', include(router.urls)),
    *custom_urlpatterns,  
]

