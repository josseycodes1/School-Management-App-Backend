from django.db import models
from accounts.models import Student, Teacher
from academics.models import Classes

# Enum-like choices for attendance status
class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    EXCUSED = "excused", "Excused"

# This model stores attendance information for each student
class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_ref = models.ForeignKey(Classes, on_delete=models.CASCADE)  # Which class the student belongs to
    date = models.DateField()  # The day this attendance was recorded
    status = models.CharField(
        max_length=10,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT
    )
    recorded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)  # Which teacher marked it
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "date")  # Prevent multiple attendance entries for same student on same day

    def __str__(self):
        return f"{self.student.user.first_name} - {self.date} - {self.status}"
