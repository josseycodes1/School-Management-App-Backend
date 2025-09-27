from django.db import models
from accounts.models import StudentProfile, TeacherProfile, ParentProfile
from django.utils import timezone
class Event(models.Model):
    title = models.CharField(max_length=255) 
    description = models.TextField()  
    date = models.DateTimeField()  
    location = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  
    def __str__(self):
        return f"{self.title} on {self.date.strftime('%Y-%m-%d')}"

class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')  
    student = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True) 
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True) 
    parent = models.ForeignKey(ParentProfile, on_delete=models.SET_NULL, null=True, blank=True)  
    registered_at = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        participant_name = self.student or self.teacher or self.parent
        return f"{participant_name} attending {self.event.title}"
