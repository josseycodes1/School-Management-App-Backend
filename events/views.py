from rest_framework import viewsets, permissions
from django.db.models import Q
from .models import Event, EventParticipant
from .serializers import (
    EventSerializer,
    EventParticipantSerializer,
    EventParticipantCreateSerializer
)
from accounts.permissions import IsAdminOrReadOnly


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
            
        return queryset

class EventParticipantViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventParticipantCreateSerializer
        return EventParticipantSerializer

    def get_queryset(self):
        queryset = EventParticipant.objects.all()
        
        # Filter by event if specified
        event_id = self.request.query_params.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
            
        # Users can only see their own participation or all if admin/teacher
        if not (self.request.user.is_staff or hasattr(self.request.user, 'teacher_profile')):
            queryset = queryset.filter(
                Q(student__user=self.request.user) |
                Q(teacher__user=self.request.user) |
                Q(parent__user=self.request.user)
            )
            
        return queryset.order_by('-registered_at')
