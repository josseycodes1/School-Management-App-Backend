from rest_framework import viewsets
from .models import Classes, Subject, Lesson
from .serializers import (
    ClassesSerializer,
    SubjectSerializer,
    LessonSerializer,
    SubjectCreateSerializer,
    LessonCreateSerializer
)
from rest_framework.permissions import IsAuthenticated

class ClassesViewSet(viewsets.ModelViewSet):
    queryset = Classes.objects.all()
    serializer_class = ClassesSerializer
    permission_classes = [IsAuthenticated]

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubjectCreateSerializer
        return SubjectSerializer

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LessonCreateSerializer
        return LessonSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        return queryset