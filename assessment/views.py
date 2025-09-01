# assessment/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Grade, Exam, Assignment, Result
from .serializers import GradeSerializer, ExamReadSerializer, AssignmentSerializer, ResultSerializer, ExamWriteSerializer
from accounts.permissions import IsAdminOrReadOnly, RolePermission
from datetime import datetime, timedelta

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminOrReadOnly]
    

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all().prefetch_related('audiences')[:50]  # limit results
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ExamReadSerializer
        return ExamWriteSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'teacher_profile'):
            return queryset.filter(teacher=self.request.user.teacher_profile)
        return queryset
    
    def perform_create(self, serializer):
        # Automatically set the teacher to the current user's teacher profile
        teacher_profile = None
        if hasattr(self.request.user, 'teacher_profile'):
            teacher_profile = self.request.user.teacher_profile
        
        # Calculate duration if start_time and end_time are provided
        data = serializer.validated_data
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        duration_minutes = data.get('duration_minutes')
        
        if start_time and end_time and not duration_minutes:
            # Calculate duration automatically
            start_dt = datetime.combine(datetime.today(), start_time)
            end_dt = datetime.combine(datetime.today(), end_time)
            
            if end_dt < start_dt:
                end_dt = end_dt + timedelta(days=1)
                
            duration = end_dt - start_dt
            duration_minutes = duration.total_seconds() // 60
            
            # Update the serializer data with calculated duration
            serializer.validated_data['duration_minutes'] = duration_minutes
        
        serializer.save(teacher=teacher_profile)
    
    def perform_update(self, serializer):
        # Calculate duration if start_time and end_time are provided but duration is not
        data = serializer.validated_data
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        duration_minutes = data.get('duration_minutes')
        
        if start_time and end_time and not duration_minutes:
            # Calculate duration automatically
            start_dt = datetime.combine(datetime.today(), start_time)
            end_dt = datetime.combine(datetime.today(), end_time)
            
            if end_dt < start_dt:
                end_dt = end_dt + timedelta(days=1)
                
            duration = end_dt - start_dt
            duration_minutes = duration.total_seconds() // 60
            
            # Update the serializer data with calculated duration
            serializer.validated_data['duration_minutes'] = duration_minutes
        
        serializer.save()

class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [RolePermission]  
    
    required_roles = ["teacher"]  
    
    def get_queryset(self):
        queryset = Assignment.objects.all()
        if hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.teacher_profile)


class ResultViewSet(viewsets.ModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [RolePermission] 
    
    required_roles = ["teacher", "student"]  
    
    def get_queryset(self):
        queryset = Result.objects.all()
        
        # Student can only see their own results
        if hasattr(self.request.user, 'student_profile'):
            return queryset.filter(student=self.request.user.student_profile)
            
        # Teacher can see results for their own exams/assignments
        elif hasattr(self.request.user, 'teacher_profile'):
            return queryset.filter(
                Q(exam__teacher=self.request.user.teacher_profile) |
                Q(assignment__teacher=self.request.user.teacher_profile)
            )
            
        return queryset.none()  # Default for users without profiles
