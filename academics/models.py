from django.db import models
from accounts.models import Teacher


# Classes Model (e.g., Primary 1, JSS2)
class Classes(models.Model):
    name = models.CharField(max_length=50, unique=True)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# Subject Model (e.g., Mathematics)
class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects'
    )
    assigned_class = models.ForeignKey(
        Classes,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'assigned_class')

    def __str__(self):
        return f"{self.name} - {self.assigned_class.name}"


# Lesson Model (Topic under a subject)
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
