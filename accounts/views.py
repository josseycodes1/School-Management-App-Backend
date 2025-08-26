from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db import connection
from .models import User, TeacherProfile, StudentProfile, ParentProfile, AdminProfile, Classes, Subject, Lesson
from .serializers import (
    UserSerializer, 
    TeacherProfileSerializer, 
    StudentProfileSerializer, 
    ParentProfileSerializer, 
    AdminProfileSerializer,
    LessonSerializer,
    StudentOnboardingSerializer,
    StudentOnboardingProgressSerializer,
    TeacherOnboardingProgressSerializer,
    TeacherOnboardingSerializer,
    ParentOnboardingSerializer,
    ParentOnboardingProgressSerializer,
    ClassesReadSerializer, 
    ClassesWriteSerializer,
    SubjectReadSerializer,
    SubjectWriteSerializer
)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdminOrReadOnly, IsStudentOnboarding
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from django.db import transaction
from django.utils.crypto import get_random_string

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ["create", "verify_email", "resend_verification"]:
            return [AllowAny()]
        return super().get_permissions()
    
    def get_authenticators(self):
        """Skip authentication for signup + verification endpoints"""
        if self.action in ["create", "verify_email", "resend_verification"]:
            return []  # no authentication required
        return super().get_authenticators()

    #shared helper method for sending verification email
    def send_verification_email(self, user):
        token = get_random_string(length=6, allowed_chars='0123456789')
        user.verification_token = token
        user.save()

        verification_link = f"{settings.FRONTEND_URL}/verify-email?email={user.email}&token={token}"


        send_mail(
            subject="Verify your email",
            message=f"Use this token: {token}\nOr click: {verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    #when a new user signs up
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        #send email once
        self.send_verification_email(user)

        return Response(
            {"message": "User created. Verification email sent."},
            status=status.HTTP_201_CREATED,
        )

    #resend verification (called with POST to /users/{id}/resend_verification/)
    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def resend_verification(self, request, pk=None):
        user = self.get_object()

        if user.is_verified:
            return Response({"error": "User already verified."}, status=400)

        self.send_verification_email(user)
        return Response({"message": "Verification email resent."})

    @action(detail=False, methods=['post'], url_path='verify-email', permission_classes=[AllowAny])
    def verify_email(self, request):
        email = request.data.get("email")
        token = request.data.get("token")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # check token
        if user.verification_token != token:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        # check expiry
        if user.verification_token_expiry and timezone.now() > user.verification_token_expiry:
            return Response({"error": "Token expired"}, status=status.HTTP_400_BAD_REQUEST)

        # mark user as verified
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expiry = None
        user.save()

        # send confirmation email
        send_mail(
            "Email Verified Successfully 🎉",
            f"Hi {user.first_name},\n\nYour email {user.email} has been verified successfully.\n\nYou can now log in to your account.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
#usercount on admin dashboard
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_counts(request):
    students_count = StudentProfile.objects.count()
    teachers_count = TeacherProfile.objects.count()
    parents_count = ParentProfile.objects.count()

    male_students = StudentProfile.objects.filter(gender="M").count()
    female_students = StudentProfile.objects.filter(gender="F").count()

    data = {
        "students": students_count,
        "teachers": teachers_count,
        "parents": parents_count,
        "male_students": male_students,
        "female_students": female_students,
    }
    return Response(data)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Check onboarding status safely
        onboarding_complete = True
        if user.role == 'student':
            try:
                profile = StudentProfile.objects.get(user=user)
                required_fields = [
                    'phone', 'address', 'gender',
                    'birth_date', 'parent_name', 'parent_name', 'class_level',
                    'photo'
                ]
                onboarding_complete = all(
                    getattr(profile, field) for field in required_fields
                )
            except StudentProfile.DoesNotExist:
                onboarding_complete = False

        return Response({
            "refresh": str(refresh),
            "access": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "onboarding_complete": onboarding_complete
            }
        }, status=status.HTTP_200_OK)
     
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
    
class StudentOnboardingView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            # Get or create student profile
            profile, created = StudentProfile.objects.get_or_create(
                user=request.user,
                defaults={'user': request.user}
            )
            
            serializer = StudentOnboardingSerializer(
                profile,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StudentOnboardingProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            serializer = StudentOnboardingProgressSerializer(student_profile)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            # Return empty progress if profile doesn't exist yet
            return Response({
                "progress": 0,
                "completed": False,
                "required_fields": {
                    'phone': False,
                    'address': False,
                    'gender': False,
                    'parent_name': False,   
                    'parent_contact': False, 
                    'birth_date': False,
                    'class_level': False,
                    'photo': False,
                    'admission_number': False
                }
            })

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly | IsStudentOnboarding]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return StudentProfile.objects.all()
        return StudentProfile.objects.filter(user=user)
    
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().select_related('teacher__user', 'assigned_class')
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return SubjectWriteSerializer
        return SubjectReadSerializer
    
    def get_queryset(self):
        """Filter subjects based on user role"""
        queryset = super().get_queryset()
        
        # If user is a teacher, only show subjects they teach
        if hasattr(self.request.user, 'teacher_profile'):
            return queryset.filter(teacher=self.request.user.teacher_profile)
        
        # If user is a student, show subjects from their class
        if hasattr(self.request.user, 'student_profile') and self.request.user.student_profile.class_level:
            return queryset.filter(assigned_class=self.request.user.student_profile.class_level)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """Get subjects by class ID"""
        class_id = request.query_params.get('class_id')
        if not class_id:
            return Response(
                {'error': 'class_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subjects = Subject.objects.filter(assigned_class_id=class_id)
        serializer = self.get_serializer(subjects, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_subjects(self, request):
        """Get subjects for the current teacher"""
        if hasattr(request.user, 'teacher_profile'):
            subjects = Subject.objects.filter(teacher=request.user.teacher_profile)
            serializer = self.get_serializer(subjects, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_200_OK)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Get profile based on user role
        profile_data = {}
        if user.role == 'teacher':
            profile = TeacherProfile.objects.get(user=user)
            profile_data = {
                'profile_image': profile.photo.url if profile.photo else None,
            }
        elif user.role == 'student':
            profile = StudentProfile.objects.get(user=user)
            profile_data = {
                'profile_image': profile.photo.url if profile.photo else None,
            }
        elif user.role == 'parent':
            profile = ParentProfile.objects.get(user=user)
            profile_data = {
                'profile_image': profile.photo.url if profile.photo else None,
            }
        elif user.role == 'admin':
            profile = AdminProfile.objects.get(user=user)
            profile_data = {
                'profile_image': profile.photo.url if profile.photo else None,
            }
        
        response_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            **profile_data
        }
        
        return Response(response_data)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LessonSerializer
        return LessonSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        return queryset
    
class AdminProfileViewSet(viewsets.ModelViewSet):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Allow any authenticated user to view
            permission_classes = [IsAuthenticated]
        else:
            # Only admin can create/update/delete
            permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
        return [permission() for permission in permission_classes]
    
class TeacherOnboardingView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            # Get or create teacher profile
            profile, created = TeacherProfile.objects.get_or_create(
                user=request.user,
                defaults={'user': request.user}
            )
            
            serializer = TeacherOnboardingSerializer(
                profile,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TeacherOnboardingProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher_profile = TeacherProfile.objects.get(user=request.user)
            serializer = TeacherOnboardingProgressSerializer(teacher_profile)
            return Response(serializer.data)
        except TeacherProfile.DoesNotExist:
            return Response({
                "progress": 0,
                "completed": False,
                "required_fields": {
                    'phone': False,
                    'address': False,
                    'gender': False,
                    'birth_date': False,
                    'subject_specialization': False,
                    'hire_date': False,
                    'photo': False
                }
            })

class ParentProfileViewSet(viewsets.ModelViewSet):
    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    
class ParentOnboardingView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            # Get or create parent profile
            profile, created = ParentProfile.objects.get_or_create(
                user=request.user,
                defaults={'user': request.user}
            )
            
            serializer = ParentOnboardingSerializer(
                profile,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ParentOnboardingProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            parent_profile = ParentProfile.objects.get(user=request.user)
            serializer = ParentOnboardingProgressSerializer(parent_profile)
            return Response(serializer.data)
        except ParentProfile.DoesNotExist:
            return Response({
                "progress": 0,
                "completed": False,
                "required_fields": {
                    'phone': False,
                    'address': False,
                    'gender': False,
                    'birth_date': False,
                    'emergency_contact': False,
                    'photo': False
                }
            })

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class ClassesViewSet(viewsets.ModelViewSet):
    queryset = Classes.objects.all().select_related('teacher__user')
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return ClassesWriteSerializer
        return ClassesReadSerializer