from rest_framework import serializers
from .models import Announcement

class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            'title', 'message', 'start_date', 'end_date', 'is_active',
            'target_students', 'target_teachers', 'target_parents'
        ]
        extra_kwargs = {
            'is_active': {'required': False, 'default': True}
        }

class AnnouncementSerializer(serializers.ModelSerializer):
    target_roles = serializers.ReadOnlyField()
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'message', 'start_date', 
            'end_date', 'is_active', 'created_at',
            'updated_at', 'target_students', 'target_teachers', 
            'target_parents', 'target_roles'
        ]
        read_only_fields = ['created_at', 'updated_at', 'target_roles']