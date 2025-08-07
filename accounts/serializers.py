from rest_framework import serializers
from .models import User, AdminProfile, TeacherProfile, StudentProfile, ParentProfile
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.db import IntegrityError
from .models import Classes, Subject, Lesson
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    verification_token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'role',
            'is_verified',
            'verification_token',
            'date_joined',
            'last_updated'
        ]
        extra_kwargs = {
            'is_verified': {'read_only': True},
            'date_joined': {'read_only': True},
            'last_updated': {'read_only': True},
            'role': {'required': True}
        }

    def create(self, validated_data):
        try:
            # Create user with all fields including verification
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                role=validated_data['role'],
                is_active=False
            )

            # Print token in development
            if settings.DEBUG:
                print(f"Verification token for {user.email}: {user.verification_token}")

            return user

        except IntegrityError as e:
            if 'email' in str(e):
                raise serializers.ValidationError({'email': 'This email already exists'})
            raise

    def send_verification_email(self, user):
        """Send verification email with token link"""
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={user.verification_token}&email={user.email}"
        try:
            send_mail(
                "Verify Your Email Address",
                f"Please click this link to verify your email: {verification_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email: {e}")

class AdminProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AdminProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TeacherProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ParentProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
        
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
        
        
class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        

class StudentOnboardingSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    photo = serializers.ImageField(required=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'email', 'first_name', 'last_name', 
            'phone', 'address', 'gender', 'birth_date',
            'photo', 'blood_type', 'parent_name', 'parent_contact',
            'class_level', 'admission_number'
        ]
        extra_kwargs = {
            'gender': {'required': True},
            'birth_date': {'required': True},
            'parent_name': {'required': True},
            'parent_contact': {'required': True},
            'class_level': {'required': True},
            'admission_number': {'required': True},
            'blood_type': {'required': False},
            'phone': {'required': True},
            'address': {'required': True},
        }

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        # Update user fields if provided
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Mark as onboarded when all required fields are filled
        required_fields = [
            'phone', 'address', 'gender',
            'birth_date', 'parent_name', 'parent_contact',
            'class_level', 'photo', 'admission_number'
        ]
        if all(getattr(instance, field) for field in required_fields):
            instance.is_onboarded = True
        
        instance.save()
        return instance

class StudentOnboardingProgressSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    required_fields = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = ['progress', 'completed', 'required_fields']

    def get_required_fields(self, obj):
        return {
            'phone': bool(obj.phone),
            'address': bool(obj.address),
            'gender': bool(obj.gender),
            'birth_date': bool(obj.birth_date),
            'parent_name': bool(obj.parent_name),
            'parent_contact': bool(obj.parent_contact),
            'class_level': bool(obj.class_level),
            'photo': bool(obj.photo),
            'admission_number': bool(obj.admission_number)
        }

    def get_completed(self, obj):
        required_fields = self.get_required_fields(obj)
        return all(required_fields.values())

    def get_progress(self, obj):
        required_fields = self.get_required_fields(obj)
        filled = sum(required_fields.values())
        total = len(required_fields)
        return int((filled / total) * 100) if total > 0 else 0
    
class TeacherOnboardingSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    photo = serializers.ImageField(required=True)
    
    class Meta:
        model = TeacherProfile
        fields = [
            'email', 'first_name', 'last_name',
            'phone', 'address', 'gender', 'birth_date',
            'photo', 'blood_type', 'subject_specialization',
            'hire_date', 'qualifications', 'is_principal'
        ]
        extra_kwargs = {
            'gender': {'required': True},
            'birth_date': {'required': True},
            'phone': {'required': True},
            'address': {'required': True},
            'subject_specialization': {'required': True},
            'hire_date': {'required': True},
            'photo': {'required': True}
        }

    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise serializers.ValidationError("Birth date cannot be in the future")
        return value

    def validate_hire_date(self, value):
        if value > datetime.now().date():
            raise serializers.ValidationError("Hire date cannot be in the future")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        # Update user fields
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class TeacherOnboardingProgressSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    required_fields = serializers.SerializerMethodField()

    class Meta:
        model = TeacherProfile
        fields = ['progress', 'completed', 'required_fields']

    def get_required_fields(self, obj):
        return {
            'phone': bool(obj.phone),
            'address': bool(obj.address),
            'gender': bool(obj.gender),
            'birth_date': bool(obj.birth_date),
            'subject_specialization': bool(obj.subject_specialization),
            'hire_date': bool(obj.hire_date),
            'photo': bool(obj.photo)
        }

    def get_completed(self, obj):
        required_fields = self.get_required_fields(obj)
        return all(required_fields.values())

    def get_progress(self, obj):
        required_fields = self.get_required_fields(obj)
        filled = sum(required_fields.values())
        total = len(required_fields)
        return int((filled / total) * 100) if total > 0 else 0
    
class ParentOnboardingSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    photo = serializers.ImageField(required=True)
    
    class Meta:
        model = ParentProfile
        fields = [
            'email', 'first_name', 'last_name',
            'phone', 'address', 'gender', 'birth_date',
            'photo', 'blood_type', 'emergency_contact',
            'occupation'
        ]
        extra_kwargs = {
            'gender': {'required': True},
            'birth_date': {'required': True},
            'phone': {'required': True},
            'address': {'required': True},
            'emergency_contact': {'required': True},
            'photo': {'required': True}
        }

    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise serializers.ValidationError("Birth date cannot be in the future")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        # Update user fields
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class ParentOnboardingProgressSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    required_fields = serializers.SerializerMethodField()

    class Meta:
        model = ParentProfile
        fields = ['progress', 'completed', 'required_fields']

    def get_required_fields(self, obj):
        return {
            'phone': bool(obj.phone),
            'address': bool(obj.address),
            'gender': bool(obj.gender),
            'birth_date': bool(obj.birth_date),
            'emergency_contact': bool(obj.emergency_contact),
            'photo': bool(obj.photo)
        }

    def get_completed(self, obj):
        required_fields = self.get_required_fields(obj)
        return all(required_fields.values())

    def get_progress(self, obj):
        required_fields = self.get_required_fields(obj)
        filled = sum(required_fields.values())
        total = len(required_fields)
        return int((filled / total) * 100) if total > 0 else 0