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
        queryset = Exam.objects.all().select_related("teacher", "subject")  # adjust to actual FKs
        if hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
        return queryset.order_by("-id")[:50]  # only return the latest 50 exams

    def perform_create(self, serializer):
        teacher_profile = getattr(self.request.user, "teacher_profile", None)

        data = serializer.validated_data
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        duration_minutes = data.get("duration_minutes")

        if start_time and end_time and not duration_minutes:
            start_dt = datetime.combine(datetime.today(), start_time)
            end_dt = datetime.combine(datetime.today(), end_time)

            if end_dt < start_dt:
                end_dt = end_dt + timedelta(days=1)

            duration = end_dt - start_dt
            duration_minutes = duration.total_seconds() // 60
            serializer.validated_data["duration_minutes"] = duration_minutes

        serializer.save(teacher=teacher_profile)

    def perform_update(self, serializer):
        data = serializer.validated_data
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        duration_minutes = data.get("duration_minutes")

        if start_time and end_time and not duration_minutes:
            start_dt = datetime.combine(datetime.today(), start_time)
            end_dt = datetime.combine(datetime.today(), end_time)

            if end_dt < start_dt:
                end_dt = end_dt + timedelta(days=1)

            duration = end_dt - start_dt
            duration_minutes = duration.total_seconds() // 60
            serializer.validated_data["duration_minutes"] = duration_minutes

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
