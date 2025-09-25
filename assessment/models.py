from django.db import models
from accounts.models import Subject, Classes
from accounts.models import StudentProfile, TeacherProfile
from datetime import datetime, timedelta

class Grade(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Exam(models.Model):
    title = models.CharField(max_length=100) 
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True) 
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True) 
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True) 
    start_time = models.TimeField(null=True, blank=True) 
    end_time = models.TimeField(null=True, blank=True) 
    duration_minutes = models.PositiveIntegerField(null=True, blank=True) 
    description = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True) 
    exam_date = models.DateField()

    def __str__(self):
        subject_name = self.subject.name if self.subject else "No Subject"
        return f"{self.title} - {subject_name}"

    def save(self, *args, **kwargs):
        
        if self.start_time and self.end_time and not self.duration_minutes:
            start_dt = datetime.combine(datetime.today(), self.start_time)
            end_dt = datetime.combine(datetime.today(), self.end_time)
            
            if end_dt < start_dt:
                end_dt = end_dt + timedelta(days=1)  
                
            duration = end_dt - start_dt
            self.duration_minutes = duration.total_seconds() // 60
            
        super().save(*args, **kwargs)


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
