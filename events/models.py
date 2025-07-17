from django.db import models
from accounts.models import Student, Teacher, Parent
from django.utils import timezone

#stores information about upcoming or past events
class Event(models.Model):
    title = models.CharField(max_length=255)  # The name of the event
    description = models.TextField()  # Detailed information about the event
    date = models.DateTimeField()  # When the event will take place
    location = models.CharField(max_length=255)  # Where the event is happening
    created_at = models.DateTimeField(auto_now_add=True)  # When the event was created
    updated_at = models.DateTimeField(auto_now=True)  # When the event was last edited

    def __str__(self):
        return f"{self.title} on {self.date.strftime('%Y-%m-%d')}"

#model keeps track of people (students, teachers, parents) who will attend the event
class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')  # Which event
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)  # Optional student
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)  # Optional teacher
    parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, blank=True)  # Optional parent
    registered_at = models.DateTimeField(default=timezone.now)  # When the person registered

    def __str__(self):
        participant_name = self.student or self.teacher or self.parent
        return f"{participant_name} attending {self.event.title}"
