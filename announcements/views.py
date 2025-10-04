from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
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

       
        if self.action in ['list', 'retrieve']:
            show_all = self.request.query_params.get('all', None)

           
            if not (show_all == 'true' and self.request.user.is_staff):
                queryset = queryset.filter(
                    Q(is_active=True) &
                    Q(start_date__lte=now) &
                    (Q(end_date__gte=now) | Q(end_date__isnull=True))
                )

             
                user_role = self.request.user.role

                if user_role == 'student':
                    queryset = queryset.filter(audiences__student__user=self.request.user)
                elif user_role == 'teacher':
                    queryset = queryset.filter(audiences__teacher__user=self.request.user)
                elif user_role == 'parent':
                    queryset = queryset.filter(audiences__parent__user=self.request.user)

        
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

class AnnouncementAudiencePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AnnouncementAudienceViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementAudienceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AnnouncementAudiencePagination

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

    def list(self, request, *args, **kwargs):
   
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)