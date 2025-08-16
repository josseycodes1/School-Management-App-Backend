# assessment/views.py
from rest_framework import viewsets
from django.db.models import Q
from .models import Grade, Exam, Assignment, Result
from .serializers import GradeSerializer, ExamSerializer, AssignmentSerializer, ResultSerializer
from accounts.permissions import IsAdminOrReadOnly, RolePermission 


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminOrReadOnly]


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [RolePermission] 
    
    required_roles = ["teacher"] 
    
    def get_queryset(self):
        queryset = Exam.objects.all()
        if hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.teacher_profile)


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
