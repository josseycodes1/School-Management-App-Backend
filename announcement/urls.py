
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementViewSet, AnnouncementAudienceViewSet

router = DefaultRouter()
router.register(r'announcements', AnnouncementViewSet, basename='announcement')  # Changed to plural
router.register(r'audiences', AnnouncementAudienceViewSet, basename='announcement-audience')

urlpatterns = [
    path('', include(router.urls)),
]