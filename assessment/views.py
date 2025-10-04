
from rest_framework import viewsets, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q
from .models import Grade, Exam, Assignment, Result
from .serializers import GradeSerializer, ExamReadSerializer, AssignmentSerializer, ResultSerializer, ExamWriteSerializer
from accounts.permissions import IsAdminOrReadOnly, RolePermission
from datetime import datetime, timedelta

class GradePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = GradePagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ExamPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ExamViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExamPagination

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
        queryset = Exam.objects.all().select_related("teacher", "subject")
        
    
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(subject__name__icontains=search)
            )

        if hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            
        return queryset.order_by("-id")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

class AssignmentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [RolePermission]  
    pagination_class = AssignmentPagination
    
    required_roles = ["teacher"]  

    def get_queryset(self):
        queryset = Assignment.objects.all()
        
      
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(subject__name__icontains=search)
            )

        if hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.teacher_profile)

class ResultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ResultViewSet(viewsets.ModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [RolePermission] 
    pagination_class = ResultPagination
    
    required_roles = ["teacher", "student"]  

    def get_queryset(self):
        queryset = Result.objects.all()
        
     
        search = self.request.query_params.get('search')
        if search and hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(exam__title__icontains=search) |
                Q(assignment__title__icontains=search)
            )

      
        if hasattr(self.request.user, 'student_profile'):
            return queryset.filter(student=self.request.user.student_profile)
            
    
        elif hasattr(self.request.user, 'teacher_profile'):
            return queryset.filter(
                Q(exam__teacher=self.request.user.teacher_profile) |
                Q(assignment__teacher=self.request.user.teacher_profile)
            )
            
        return queryset.none()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)