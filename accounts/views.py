from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import User, TeacherProfile, StudentProfile, ParentProfile, AdminProfile
from .serializers import (
    UserSerializer, 
    TeacherProfileSerializer, 
    StudentProfileSerializer, 
    ParentProfileSerializer, 
    AdminProfileSerializer
)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdminOrReadOnly
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import uuid

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'verify_email', 'resend_verification']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='resend_verification')
    def resend_verification(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email, is_verified=False)
            token = user.generate_verification_token()
            
            if settings.DEBUG:
                print(f"New verification token for {email}: {token}")

            send_mail(
                "Your New Verification Code",
                f"Your new verification code is: {token}\n\n"
                f"Please enter this code to complete your registration.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({
                "message": "New verification code sent successfully"
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": "Email not found or already verified"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='verify_email', permission_classes=[AllowAny])
    def verify_email(self, request):
        token = request.data.get('token')
        email = request.data.get('email')

        if not token or not email:
            return Response({"error": "Token and email are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, verification_token=token)

            if user.is_verification_token_expired:
                return Response({"error": "Verification token has expired"}, status=status.HTTP_400_BAD_REQUEST)

            user.verify_user()

            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Invalid token or email"}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if email is None or password is None:
            return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }, status=status.HTTP_200_OK)

class AdminProfileViewSet(viewsets.ModelViewSet):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

class ParentProfileViewSet(viewsets.ModelViewSet):
    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email required"}, status=400)

        try:
            user = User.objects.get(email=email)
            token = user.generate_password_reset_token()
            
            if settings.DEBUG:
                print(f"Password reset token for {email}: {token}")

            send_mail(
                "Your Password Reset Code",
                f"Enter this code to reset your password: {token}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({"message": "Reset code sent to email"}, status=200)
            
        except User.DoesNotExist:
            return Response({"error": "Email not found"}, status=404)

class PasswordResetVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not all([token, email, new_password]):
            return Response({"error": "Token, email and new password are required"}, 
                          status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(
                email=email,
                password_reset_token=token
            )

            if timezone.now() > (user.password_reset_token_created_at + timedelta(hours=24)):
                user.password_reset_token = None
                user.password_reset_token_created_at = None
                user.save()
                return Response({"error": "Password reset link has expired"},
                              status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_token_created_at = None
            user.save()

            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Invalid reset token or email"},
                          status=status.HTTP_400_BAD_REQUEST)

class PasswordResetResendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.generate_password_reset_token()
            user.save()
            
            if settings.DEBUG:
                print(f"New reset token for {email}: {user.password_reset_token}")

            return Response({"message": "Password reset link resent"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=400)
        
        try:
            user = User.objects.get(email=email, is_verified=False)
            token = user.generate_verification_token()
            return Response({
                "message": "Verification code resent",
                "token": token
            })
        except User.DoesNotExist:
            return Response({"error": "Email not found or already verified"}, status=400)
