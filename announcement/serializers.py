from rest_framework import serializers
from .models import Announcement, AnnouncementAudience
from accounts.serializers import (
    StudentProfileSerializer,
    TeacherProfileSerializer,
    ParentProfileSerializer
)

class AnnouncementAudienceSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    teacher = TeacherProfileSerializer(read_only=True)
    parent = ParentProfileSerializer(read_only=True)
    
    class Meta:
        model = AnnouncementAudience
        fields = ['id', 'announcement', 'student', 'teacher', 'parent']
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