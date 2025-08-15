from django.db import models
from accounts.models import Subject, Classes
from accounts.models import StudentProfile, TeacherProfile

# Grade model 
class Grade(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Exam model
class Exam(models.Model):
    title = models.CharField(max_length=100)  # Name of the exam e.g., "First Term Math Exam"
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)  # Related subject
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)  # Who created/owns this exam
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)  # Grade this exam is meant for
    exam_date = models.DateField()  # Date the exam is scheduled
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically adds creation timestamp

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

# Assignment model
class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True )
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Result model
class Result(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)  # allows scores like 98.50
    graded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.exam:
            return f"{self.student.user.first_name} - {self.exam.title}"
        elif self.assignment:
            return f"{self.student.user.first_name} - {self.assignment.title}"
        return f"{self.student.user.first_name} - No assessment"
