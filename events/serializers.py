from rest_framework import serializers
from .models import Event, EventParticipant
from accounts.serializers import (
    StudentProfileSerializer,
    TeacherProfileSerializer,
    ParentProfileSerializer
)

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class EventParticipantSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    student = StudentProfileSerializer(read_only=True)
    teacher = TeacherProfileSerializer(read_only=True)
    parent = ParentProfileSerializer(read_only=True)

    class Meta:
        model = EventParticipant
        fields = '__all__'

class EventParticipantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventParticipant
        fields = ['event', 'student', 'teacher', 'parent']
        extra_kwargs = {
            'student': {'required': False},
            'teacher': {'required': False},
            'parent': {'required': False}
        }

    def validate(self, data):
        # Ensure at least one participant type is selected
        if not any([data.get('student'), data.get('teacher'), data.get('parent')]):
            raise serializers.ValidationError(
                "At least one participant (student, teacher or parent) must be specified"
            )
        return data