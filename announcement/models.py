from django.db import models
from accounts.models import StudentProfile, TeacherProfile, ParentProfile
from django.utils import timezone

#stores the announcement content and metadata
class Announcement(models.Model):
    title = models.CharField(max_length=255)  # Title of the announcement
    message = models.TextField()  # Main announcement body
    created_at = models.DateTimeField(auto_now_add=True)  # When it was first posted
    updated_at = models.DateTimeField(auto_now=True)  # Last time it was updated
    start_date = models.DateTimeField(default=timezone.now)  # When to start showing it
    end_date = models.DateTimeField(null=True, blank=True)  # Optional end time
    is_active = models.BooleanField(default=True)  # Whether it's currently shown

    def __str__(self):
        return self.title

#tracks who the announcement is for
class AnnouncementAudience(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='audiences')
    student = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(ParentProfile, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        target = self.student or self.teacher or self.parent
        return f"Audience for {self.announcement.title}: {target}"
