from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementViewSet, AnnouncementAudienceViewSet

router = DefaultRouter()
router.register(r'announcement', AnnouncementViewSet)
router.register(r'audiences', AnnouncementAudienceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]