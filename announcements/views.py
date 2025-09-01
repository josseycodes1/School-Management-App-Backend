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
from django.db.models import Q
from django.utils import timezone


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AnnouncementCreateSerializer
        return AnnouncementSerializer

    def get_queryset(self):
        queryset = Announcement.objects.all().prefetch_related('audiences')[:50]  # limit results
        now = timezone.now()

        # Only filter for LIST or RETRIEVE when not showing all
        if self.action in ['list', 'retrieve']:
            show_all = self.request.query_params.get('all', None)

            # Admins can see all if requested
            if not (show_all == 'true' and self.request.user.is_staff):
                queryset = queryset.filter(
                    Q(is_active=True) &
                    Q(start_date__lte=now) &
                    (Q(end_date__gte=now) | Q(end_date__isnull=True))
                )

                # Restrict by audience for non-admin/non-teacher users
                user_role = self.request.user.role

                if user_role == 'student':
                    queryset = queryset.filter(audiences__student__user=self.request.user)
                elif user_role == 'teacher':
                    queryset = queryset.filter(audiences__teacher__user=self.request.user)
                elif user_role == 'parent':
                    queryset = queryset.filter(audiences__parent__user=self.request.user)


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