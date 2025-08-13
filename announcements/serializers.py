from rest_framework import serializers
from .models import Announcement, AnnouncementAudience
from accounts.serializers import (
    StudentProfileSerializer,
    TeacherProfileSerializer,
    ParentProfileSerializer
)

class AnnouncementAudienceSerializer(serializers.ModelSerializer):
    student_first_name = serializers.CharField(source='student.user.first_name', read_only=True)
    student_last_name = serializers.CharField(source='student.user.last_name', read_only=True)

    teacher_first_name = serializers.CharField(source='teacher.user.first_name', read_only=True)
    teacher_last_name = serializers.CharField(source='teacher.user.last_name', read_only=True)

    parent_first_name = serializers.CharField(source='parent.user.first_name', read_only=True)
    parent_last_name = serializers.CharField(source='parent.user.last_name', read_only=True)

    class Meta:
        model = AnnouncementAudience
        fields = [
            'id', 'announcement',
            'student_first_name', 'student_last_name',
            'teacher_first_name', 'teacher_last_name',
            'parent_first_name', 'parent_last_name'
        ]
        read_only_fields = ['announcement']
        
        
class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'start_date', 'end_date', 'is_active']  # All required fields
        extra_kwargs = {
            'is_active': {'required': False, 'default': True}  # Example optional field
        }

class AnnouncementSerializer(serializers.ModelSerializer):
    audiences = AnnouncementAudienceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'message', 'start_date', 
            'end_date', 'is_active', 'created_at',
            'updated_at', 'audiences'
        ]
        read_only_fields = ['created_at', 'updated_at']

class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'start_date', 'end_date', 'is_active']

class AudienceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementAudience
        fields = ['student', 'teacher', 'parent']