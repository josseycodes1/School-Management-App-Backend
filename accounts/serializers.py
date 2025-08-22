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
    user = UserSerializer()
    class Meta:
        model = TeacherProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        # Create user first
        password = user_data.pop("password", None)
        user = User.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()

        # Create teacher profile
        teacher_profile = TeacherProfile.objects.create(user=user, **validated_data)
        return teacher_profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                if attr == "password":
                    instance.user.set_password(value)
                else:
                    setattr(instance.user, attr, value)
            instance.user.save()

        return super().update(instance, validated_data) 
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
class ClassesReadSerializer(serializers.ModelSerializer):
    """Serializer for READ operations - includes nested teacher details"""
    teacher = TeacherProfileSerializer(read_only=True)
    
    class Meta:
        model = Classes
        fields = ['id', 'name', 'teacher', 'created_at']
        read_only_fields = ['created_at']

class ClassesWriteSerializer(serializers.ModelSerializer):
    """Serializer for WRITE operations - accepts teacher ID"""
    teacher_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Classes
        fields = ['id', 'name', 'teacher_id', 'created_at']
        read_only_fields = ['created_at']
    
    def create(self, validated_data):
        teacher_id = validated_data.pop('teacher_id', None)
        teacher = None
        
        if teacher_id:
            try:
                teacher = TeacherProfile.objects.get(id=teacher_id)
            except TeacherProfile.DoesNotExist:
                raise serializers.ValidationError({
                    'teacher_id': f"Teacher with ID {teacher_id} does not exist."
                })
        
        return Classes.objects.create(teacher=teacher, **validated_data)
    
    def update(self, instance, validated_data):
        teacher_id = validated_data.pop('teacher_id', None)
        teacher = None
        
        if teacher_id is not None:  # Handle both setting and nullifying
            if teacher_id:
                try:
                    teacher = TeacherProfile.objects.get(id=teacher_id)
                except TeacherProfile.DoesNotExist:
                    raise serializers.ValidationError({
                        'teacher_id': f"Teacher with ID {teacher_id} does not exist."
                    })
            # If teacher_id is null/empty, teacher remains None
        
        instance.name = validated_data.get('name', instance.name)
        instance.teacher = teacher
        instance.save()
        return instance

class SubjectReadSerializer(serializers.ModelSerializer):
    """Serializer for READ operations - includes nested teacher details"""
    teacher = TeacherProfileSerializer(read_only=True)
    assigned_class_name = serializers.CharField(source='assigned_class.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'teacher', 'assigned_class', 'assigned_class_name', 'created_at']
        read_only_fields = ['created_at']

class SubjectWriteSerializer(serializers.ModelSerializer):
    """Serializer for WRITE operations - accepts teacher ID and class ID"""
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=TeacherProfile.objects.all(),
        source='teacher',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'teacher_id', 'assigned_class', 'created_at']
        read_only_fields = ['created_at']
    
    def validate(self, data):
        """Validate that the subject name is unique within the same class"""
        name = data.get('name')
        assigned_class = data.get('assigned_class')
        
        if name and assigned_class:
            # Check if subject with same name already exists in this class
            existing_subject = Subject.objects.filter(
                name=name, 
                assigned_class=assigned_class
            ).exclude(id=self.instance.id if self.instance else None).exists()
            
            if existing_subject:
                raise serializers.ValidationError({
                    'name': 'A subject with this name already exists in this class.'
                })
        
        return data

class LessonSerializer(serializers.ModelSerializer):
    subject = SubjectWriteSerializer(read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'subject', 'date', 'created_at']
        read_only_fields = ['created_at']
        
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        # Create user first
        password = user_data.pop("password", None)
        user = User.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()
            
         # Create teacher profile
        teacher_profile = TeacherProfile.objects.create(user=user, **validated_data)
        return teacher_profile
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                if attr == "password":
                    instance.user.set_password(value)
                else:
                    setattr(instance.user, attr, value)
            instance.user.save()

        return super().update(instance, validated_data)  
class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False)

    class Meta:
        model = StudentProfile
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        # Create user first
        password = user_data.pop("password", None)
        user = User.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()

        # Create student profile
        student_profile = StudentProfile.objects.create(user=user, **validated_data)
        return student_profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_data:
            user = instance.user
            if "password" in user_data:
                user.set_password(user_data["password"])
                user_data.pop("password")
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance
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
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
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
class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = ParentProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        # Create user first
        password = user_data.pop("password", None)
        user = User.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()
            
        # Create parent profile
        parent_profile = ParentProfile.objects.create(user=user, **validated_data)
        return parent_profile
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_data:
            user = instance.user
            if "password" in user_data:
                user.set_password(user_data["password"])
                user_data.pop("password")
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance
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