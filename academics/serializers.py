from rest_framework import serializers
from .models import Classes, Subject, Lesson
from accounts.serializers import TeacherProfileSerializer

class ClassesSerializer(serializers.ModelSerializer):
    teacher = TeacherProfileSerializer(read_only=True)
    
    class Meta:
        model = Classes
        fields = ['id', 'name', 'teacher', 'created_at']
        read_only_fields = ['created_at']

class SubjectSerializer(serializers.ModelSerializer):
    teacher = TeacherProfileSerializer(read_only=True)
    assigned_class = ClassesSerializer(read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'teacher', 'assigned_class', 'created_at']
        read_only_fields = ['created_at']

class LessonSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'subject', 'date', 'created_at']
        read_only_fields = ['created_at']

# For creating/updating (simplified versions)
class SubjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['name', 'teacher', 'assigned_class']

class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'subject', 'date']