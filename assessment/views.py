# assessment/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Grade, Exam, Assignment, Result
from .serializers import GradeSerializer, ExamReadSerializer, AssignmentSerializer, ResultSerializer, ExamWriteSerializer
from accounts.permissions import IsAdminOrReadOnly, RolePermission


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminOrReadOnly]
    

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all().select_related('subject', 'teacher', 'grade')
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
    
    # EXPLICITLY ADD UPDATE METHODS
    def update(self, request, *args, **kwargs):
        """Handle PUT requests"""
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests"""
        return super().partial_update(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'teacher_profile'):
            return queryset.filter(teacher=self.request.user.teacher_profile)
        return queryset
    
    def perform_create(self, serializer):
        if hasattr(self.request.user, 'teacher_profile'):
            serializer.save(teacher=self.request.user.teacher_profile)
        else:
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
