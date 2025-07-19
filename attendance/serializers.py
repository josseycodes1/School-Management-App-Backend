from rest_framework import serializers
from .models import AttendanceRecord, AttendanceStatus
from accounts.serializers import StudentProfileSerializer, TeacherProfileSerializer
from academics.serializers import ClassesSerializer

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    class_ref = ClassesSerializer(read_only=True)
    recorded_by = TeacherProfileSerializer(read_only=True)
    status = serializers.ChoiceField(choices=AttendanceStatus.choices)

    class Meta:
        model = AttendanceRecord
        fields = '__all__'
        extra_kwargs = {
            'student': {'required': True},
            'class_ref': {'required': True},
            'date': {'required': True}
        }

class AttendanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ['student', 'class_ref', 'date', 'status']