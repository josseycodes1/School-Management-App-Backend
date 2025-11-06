
from rest_framework import serializers
from .models import Grade, Exam, Assignment, Result
from accounts.models import TeacherProfile, Subject
from accounts.serializers import SubjectWriteSerializer
from accounts.serializers import TeacherProfileSerializer, StudentProfileSerializer, SubjectWriteSerializer

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

class ExamReadSerializer(serializers.ModelSerializer):
    subject = SubjectWriteSerializer(read_only=True)
    teacher = TeacherProfileSerializer(read_only=True)
    grade = GradeSerializer(read_only=True)
    
    class Meta:
        model = Exam
        fields = '__all__'

class ExamWriteSerializer(serializers.ModelSerializer):
   
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        required=True
    )
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=TeacherProfile.objects.all(),
        required=False  
    )
    grade = serializers.PrimaryKeyRelatedField(
        queryset=Grade.objects.all(),
        required=False  
    )
    
    class Meta:
        model = Exam
        fields = ['title', 'subject', 'teacher', 'grade', 'exam_date', 
                 'start_time', 'end_time', 'duration_minutes', 'description']
class AssignmentSerializer(serializers.ModelSerializer):
    subject = SubjectWriteSerializer(read_only=True)
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
    exam = ExamWriteSerializer(read_only=True)
    assignment = AssignmentSerializer(read_only=True)
    
    class Meta:
        model = Result
        fields = '__all__'
        extra_kwargs = {
            'student': {'required': True}
        }