from django.db import models
from accounts.models import StudentProfile, TeacherProfile
from accounts.models import Classes


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    EXCUSED = "excused", "Excused"

class AttendanceRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    class_ref = models.ForeignKey(Classes, on_delete=models.CASCADE) 
    date = models.DateField()  
    status = models.CharField(
        max_length=10,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT
    )
    recorded_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "date")  

    def __str__(self):
        return f"{self.student.user.first_name} - {self.date} - {self.status}"
