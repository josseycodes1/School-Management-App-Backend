from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Announcement
from .serializers import (
    AnnouncementSerializer,
    AnnouncementCreateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from accounts.permissions import IsAdminOrReadOnly

class AnnouncementPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AnnouncementPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AnnouncementCreateSerializer
        return AnnouncementSerializer

    def get_queryset(self):
        queryset = Announcement.objects.all()
        now = timezone.now()
        user = self.request.user

        if self.action in ['list', 'retrieve']:
            show_all = self.request.query_params.get('all', None)

            # If user is staff and explicitly requests all announcements, show everything
            if not (show_all == 'true' and user.is_staff):
                # Filter by active status and date range
                queryset = queryset.filter(
                    Q(is_active=True) &
                    Q(start_date__lte=now) &
                    (Q(end_date__gte=now) | Q(end_date__isnull=True))
                )

                # Filter by user's role
                user_role = user.role
                if user_role == 'student':
                    queryset = queryset.filter(target_students=True)
                elif user_role == 'teacher':
                    queryset = queryset.filter(target_teachers=True)
                elif user_role == 'parent':
                    queryset = queryset.filter(target_parents=True)

        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(message__icontains=search)
            ).distinct()

        return queryset.order_by('-start_date')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)