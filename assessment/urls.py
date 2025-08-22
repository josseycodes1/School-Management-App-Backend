from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GradeViewSet,
    ExamViewSet,
    AssignmentViewSet,
    ResultViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'results', ResultViewSet, basename='result')


# Custom endpoints can be added here if needed
custom_urlpatterns = [
    # Example: path('reports/', include('assessment.reports.urls')),
]

urlpatterns = [
    path('', include(router.urls)),
    *custom_urlpatterns,  # Include any additional patterns
]

