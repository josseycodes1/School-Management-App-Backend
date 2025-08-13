from rest_framework import viewsets
from django.db.models import Q
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer, AttendanceCreateSerializer
from accounts.permissions import IsAdminOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils.timezone import now, timedelta

from .models import AttendanceRecord, AttendanceStatus

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_attendance_summary(request):
    today = now().date()
    start_date = today - timedelta(days=6)  # Last 7 days including today

    records = (
        AttendanceRecord.objects
        .filter(date__range=[start_date, today])
        .values('date')
        .annotate(
            present_count=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
            absent_count=Count('id', filter=Q(status=AttendanceStatus.ABSENT))
        )
        .order_by('date')
    )

    # Convert to a list for JSON response
    data = [
        {
            'date': r['date'],
            'present': r['present_count'],
            'absent': r['absent_count']
        }
        for r in records
    ]
    return Response(data)

class SomeViewSet(viewsets.ModelViewSet):
   permission_classes = [IsAdminOrReadOnly]
queryset = AttendanceRecord.objects.all()


class AttendanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    
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