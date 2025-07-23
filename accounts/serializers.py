from rest_framework import serializers
from .models import User, AdminProfile, TeacherProfile, StudentProfile, ParentProfile
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import uuid

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    verification_token = serializers.CharField(read_only=True)  # Expose token in dev mode

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
            'verification_token'  # Include the token field
        ]
        extra_kwargs = {
            'is_verified': {'read_only': True},
            'role': {'required': True}
        }

    def create(self, validated_data):
        # Extract password and generate token
        password = validated_data.pop('password')
        verification_token = str(uuid.uuid4())
        
        # Create user with verification token
        user = User.objects.create_user(
            password=password,
            verification_token=verification_token,
            verification_token_created_at=timezone.now(),
            is_active=False,
            **validated_data
        )

        # Development vs Production handling
        if settings.DEBUG:
            # In development: expose token in response
            user.verification_token = verification_token
            print(f"DEV MODE: Verification token for {user.email}: {verification_token}")
        else:
            # In production: send email normally
            self.send_verification_email(user)
        
        return user

    def send_verification_email(self, user):
        """Send verification email with token link"""
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={user.verification_token}"
        try:
            send_mail(
                "Verify Your Email",
                f"Click to verify your account: {verification_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log email sending errors but don't fail user creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email: {e}")

# Profile serializers remain unchanged
class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = TeacherProfile
        fields = '__all__'
        
class AdminProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = AdminProfile
        fields = '__all__' 

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = StudentProfile
        fields = '__all__'

class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ParentProfile
        fields = '__all__'