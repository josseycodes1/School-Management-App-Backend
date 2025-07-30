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
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .permissions import IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'verify_email']:
            return [AllowAny()]
        return [IsAuthenticated()]

    # Changed to use @action properly without conflicting with existing routes
    @action(detail=False, methods=['post'], url_path='verify_email')
    def verify_email(self, request):
        token = request.data.get('token')
        email = request.data.get('email')
        
        if not token or not email:
            return Response(
                {"error": "Token and email are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(
                email=email,
                verification_token=token
            )

            if user.is_verification_token_expired:
                user.verification_token = None
                user.verification_token_created_at = None
                user.save()
                return Response(
                    {"error": "Verification link has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )

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
                {"error": "Invalid verification token or email"},
                status=status.HTTP_400_BAD_REQUEST
            )

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