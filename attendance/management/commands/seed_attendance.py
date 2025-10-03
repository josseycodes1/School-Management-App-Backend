from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from attendance.models import AttendanceRecord, AttendanceStatus
from accounts.models import StudentProfile, TeacherProfile, Classes
import random
from datetime import timedelta

fake = Faker()

class Command(BaseCommand):
    help = "Seed attendance records for students"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of past days to generate attendance for'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all attendance records before seeding'
        )

    def handle(self, *args, **options):
        if not StudentProfile.objects.exists():
            self.stdout.write(self.style.ERROR("❌ No students found. Run accounts seed first!"))
            return

        if options['clear']:
            AttendanceRecord.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Cleared all attendance records."))

        self.create_attendance_records(options['days'])
        self.stdout.write(self.style.SUCCESS(f"✅ Created attendance records for {options['days']} days!"))

    def create_attendance_records(self, days_back):
        students = list(StudentProfile.objects.all())
        teachers = list(TeacherProfile.objects.all())
        classes = list(Classes.objects.all())

        for days_ago in range(1, days_back + 1):
            date = timezone.now().date() - timedelta(days=days_ago)
            
            # Skip weekends (optional)
            if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                continue

            for student in random.sample(students, k=int(len(students)*0.8)):  # 80% attendance each day
                try:
                    AttendanceRecord.objects.create(
                        student=student,
                        class_ref=random.choice(classes),
                        date=date,
                        status=random.choices(
                            [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.LATE, AttendanceStatus.EXCUSED],
                            weights=[85, 8, 5, 2],  # Probability weights
                            k=1
                        )[0],
                        recorded_by=random.choice(teachers)
                    )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ Skipped attendance for {student}: {e}"))