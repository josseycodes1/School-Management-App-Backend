from rest_framework import viewsets
from django.db.models import Q
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer, AttendanceCreateSerializer
from accounts.permissions import IsTeacherOrAdmin  # Updated import

class AttendanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTeacherOrAdmin]  # Simplified permission
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AttendanceCreateSerializer
        return AttendanceRecordSerializer

    def get_queryset(self):
        queryset = AttendanceRecord.objects.all()
        
        # Date filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        
        # Teacher-specific filtering
        if hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(
                Q(recorded_by=self.request.user.teacher_profile) |
                Q(class_ref__teacher=self.request.user.teacher_profile)
            )
        
        # Class filtering
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(class_ref_id=class_id)
            
        return queryset.order_by('-date')

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'teacher_profile'):
            serializer.save(recorded_by=self.request.user.teacher_profile)
        else:
            serializer.save()