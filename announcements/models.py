from django.db import models
from accounts.models import StudentProfile, TeacherProfile, ParentProfile
from django.utils import timezone

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Role-based audience fields
    target_students = models.BooleanField(default=False)
    target_teachers = models.BooleanField(default=False)
    target_parents = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def target_roles(self):
        roles = []
        if self.target_students:
            roles.append('student')
        if self.target_teachers:
            roles.append('teacher')
        if self.target_parents:
            roles.append('parent')
        return roles
