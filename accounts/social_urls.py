from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocialMediaLinkViewSet

router = DefaultRouter()
router.register(r'links', SocialMediaLinkViewSet, basename='social-links')

urlpatterns = [
    path('', include(router.urls)),
    path('links/', SocialMediaLinkViewSet.as_view({'get': 'list'}), name='social-links'),
    path('links', SocialMediaLinkViewSet.as_view({'get': 'list'}), name='social-links-no-slash'),
]