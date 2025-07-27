from rest_framework import viewsets
from .models import Announcement, AnnouncementAudience
from .serializers import (
    AnnouncementSerializer,
    AnnouncementCreateSerializer,
    AnnouncementAudienceSerializer,
    AudienceCreateSerializer
)
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from accounts.permissions import IsAdminOrReadOnly


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AnnouncementCreateSerializer
        return AnnouncementSerializer

    def get_queryset(self):
        queryset = Announcement.objects.all()
        
        # Filter by active status
        active_only = self.request.query_params.get('active', None)
        if active_only == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                Q(is_active=True) &
                Q(start_date__lte=now) &
                (Q(end_date__gte=now) | Q(end_date__isnull=True))
            )
        
        return queryset.order_by('-start_date')

class AnnouncementAudienceViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementAudienceSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AudienceCreateSerializer
        return AnnouncementAudienceSerializer

    def get_queryset(self):
        queryset = AnnouncementAudience.objects.all()
        announcement_id = self.request.query_params.get('announcement')
        if announcement_id:
            queryset = queryset.filter(announcement_id=announcement_id)
        return queryset