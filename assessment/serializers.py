
from rest_framework import serializers
from .models import Grade, Exam, Assignment, Result
from accounts.serializers import SubjectSerializer
from accounts.serializers import TeacherProfileSerializer, StudentProfileSerializer

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherProfileSerializer(read_only=True)
    grade = GradeSerializer(read_only=True)
    
    class Meta:
        model = Exam
        fields = '__all__'
        extra_kwargs = {
            'teacher': {'required': True},
            'subject': {'required': True},
            'grade': {'required': True}
        }

class AssignmentSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherProfileSerializer(read_only=True)
    grade = GradeSerializer(read_only=True)
    
    class Meta:
        model = Assignment
        fields = '__all__'
        extra_kwargs = {
            'teacher': {'required': True},
            'subject': {'required': True},
            'grade': {'required': True}
        }

class ResultSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)
    assignment = AssignmentSerializer(read_only=True)
    
    class Meta:
        model = Result
        fields = '__all__'
        extra_kwargs = {
            'student': {'required': True}
        }