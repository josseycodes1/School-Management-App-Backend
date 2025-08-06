import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta

class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"
    PREFER_NOT_TO_SAY = "N", "Prefer not to say"

class UserRole(models.TextChoices):
    ADMIN = "admin", "Administrator"
    PARENT = "parent", "Parent"
    TEACHER = "teacher", "Teacher"
    STUDENT = "student", "Student"

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if not extra_fields.get('is_verified', False):
            user.generate_verification_token()
            
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)
        
        if extra_fields.get("role") != UserRole.ADMIN:
            raise ValueError("Superuser must have role of Admin")
            
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=UserRole.choices)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    verification_token_created_at = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    password_reset_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    password_reset_token_created_at = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]
    
    def generate_password_reset_token(self):
        self.password_reset_token = uuid.uuid4().hex 
        self.password_reset_token_created_at = timezone.now()
        self.save(update_fields=['password_reset_token', 'password_reset_token_created_at'])
        return self.password_reset_token 

    @property 
    def is_password_reset_token_expired(self):
        if not self.password_reset_token_created_at:
            return True
        return timezone.now() > (self.password_reset_token_created_at + timedelta(hours=24))

    def generate_verification_token(self):
        self.verification_token = uuid.uuid4().hex
        self.verification_token_created_at = timezone.now()
        self.save(update_fields=['verification_token', 'verification_token_created_at'])
        return self.verification_token

    @property
    def is_verification_token_expired(self):
        if not self.verification_token_created_at:
            return True
        return timezone.now() > (self.verification_token_created_at + timedelta(hours=24))

    def verify_user(self):
        self.is_verified = True
        self.is_active = True
        self.verification_token = None
        self.verification_token_created_at = None
        self.save()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['verification_token']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

class ProfileMixin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="%(class)s_profile")
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    blood_type = models.CharField(max_length=3, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user}'s Profile"

class AdminProfile(ProfileMixin):
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)

class ParentProfile(ProfileMixin):
    emergency_contact = models.CharField(max_length=15, blank=True)
    occupation = models.CharField(max_length=100, blank=True)

class TeacherProfile(ProfileMixin):
    subject_specialization = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    qualifications = models.TextField(blank=True)
    is_principal = models.BooleanField(default=False)

class StudentProfile(ProfileMixin):
    parent = models.ForeignKey(
        'User',  
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={"role": UserRole.PARENT},
        related_name="children"
    )
    admission_number = models.CharField(max_length=20, unique=True)
    class_level = models.CharField(max_length=50, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)
    medical_notes = models.TextField(blank=True)
    is_onboarded = models.BooleanField(default=False)
    photo = models.ImageField(
        upload_to='profile_photos/',
        null=False,  # No longer nullable
        blank=False,  # Not optional
        verbose_name="Profile Photo"
    )


    
    
# Classes Model (e.g., Primary 1, JSS2)
class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)  # "2024/2025"
    current = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Classes(models.Model):
    name = models.CharField(max_length=50, unique=True)
    teacher = models.ForeignKey(
        'accounts.TeacherProfile',  # Changed to string reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        'accounts.TeacherProfile',  # Changed to string reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects'
    )
    assigned_class = models.ForeignKey(
        'Classes',  # Self-reference
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'assigned_class')

    def __str__(self):
        return f"{self.name} - {self.assigned_class.name}"

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"