import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


# Enums
class UserSex(models.TextChoices):
    MALE = "Male", "Male"
    FEMALE = "Female", "Female"
    OTHER = "Other", "Other"


# Roles
USER_ROLES = (
    ('admin', 'Admin'),
    ('parent', 'Parent'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
)


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=USER_ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    def __str__(self):
        return f"{self.email} ({self.role})"


# Admin Model
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"Admin: {self.user.email}"


# Parent Model
class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Parent: {self.name} {self.surname}"


# Teacher Model
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField()
    img = models.URLField(null=True, blank=True)
    blood_type = models.CharField(max_length=10)
    sex = models.CharField(max_length=6, choices=UserSex.choices)
    birthday = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Teacher: {self.name} {self.surname}"


# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField()
    img = models.URLField(null=True, blank=True)
    blood_type = models.CharField(max_length=10)
    sex = models.CharField(max_length=6, choices=UserSex.choices)
    birthday = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="students")

    # grade and class will be added later from other apps
    def __str__(self):
        return f"Student: {self.name} {self.surname}"

