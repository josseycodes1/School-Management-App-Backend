from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from .models import User, TeacherProfile, StudentProfile, ParentProfile, AdminProfile
from .serializers import (
    UserSerializer, 
    TeacherProfileSerializer, 
    StudentProfileSerializer, 
    ParentProfileSerializer, 
    AdminProfileSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'verify_email']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def verify_email(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(verification_token=token)
            
            if user.is_verification_token_expired:
                # Clear the expired token
                user.verification_token = None
                user.verification_token_created_at = None
                user.save()
                return Response(
                    {"error": "Verification link has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark user as verified and active
            user.is_verified = True
            user.is_active = True
            user.verification_token = None
            user.verification_token_created_at = None
            user.save()
            
            return Response({
                "message": "Email successfully verified",
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid verification token"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
            



class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class ParentProfileViewSet(viewsets.ModelViewSet):
    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class AdminProfileViewSet(viewsets.ModelViewSet):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAuthenticated]