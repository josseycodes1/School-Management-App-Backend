from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, EventParticipantViewSet

router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')
router.register(r'participants', EventParticipantViewSet, basename='eventparticipant')

urlpatterns = [
    path('', include(router.urls)),
]