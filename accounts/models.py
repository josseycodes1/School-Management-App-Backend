import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    

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
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        
        if extra_fields.get("role") != UserRole.ADMIN:
            raise ValueError("Superuser must have role of Admin")
            
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=UserRole.choices)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

class ProfileMixin(models.Model):
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    photo_url = models.URLField(blank=True, null=True)
    blood_type = models.CharField(max_length=3, blank=True)

    class Meta:
        abstract = True

class AdminProfile(ProfileMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    
    class Meta:
        verbose_name = "Administrator Profile"

class ParentProfile(ProfileMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parent_profile")
    emergency_contact = models.CharField(max_length=15, blank=True)

class TeacherProfile(ProfileMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    subject_specialization = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)

class StudentProfile(ProfileMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    parent = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={"role": UserRole.PARENT},
        related_name="children"
    )
    admission_number = models.CharField(max_length=20, unique=True)