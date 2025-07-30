from rest_framework import serializers
from .models import User, AdminProfile, TeacherProfile, StudentProfile, ParentProfile
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.db import IntegrityError
from django.utils import timezone

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

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='parent'),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ParentProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']