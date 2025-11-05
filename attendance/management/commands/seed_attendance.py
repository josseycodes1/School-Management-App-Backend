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
    # Debug: Check AttendanceStatus values
        self.stdout.write("🔍 Checking AttendanceStatus values:")
        try:
            statuses = [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.LATE, AttendanceStatus.EXCUSED]
            for status in statuses:
                self.stdout.write(f"   - {status} (value: {status.value if hasattr(status, 'value') else status})")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error checking AttendanceStatus: {e}"))
        
        if not StudentProfile.objects.exists():
            self.stdout.write(self.style.ERROR("❌ No students found. Run accounts seed first!"))
            return

        if options['clear']:
            AttendanceRecord.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Cleared all attendance records."))

        self.create_attendance_records(options['days'])
        self.stdout.write(self.style.SUCCESS(f"✅ Completed attendance seeding for {options['days']} days!"))

    def create_attendance_records(self, days_back):
        students = list(StudentProfile.objects.all())
        teachers = list(TeacherProfile.objects.all())
        classes = list(Classes.objects.all())
        
        # Add debug information
        self.stdout.write(f"📊 Found {len(students)} students, {len(teachers)} teachers, {len(classes)} classes")
        
        if not students or not teachers or not classes:
            self.stdout.write(self.style.ERROR("❌ Missing required data:"))
            if not students:
                self.stdout.write(self.style.ERROR("   - No students found"))
            if not teachers:
                self.stdout.write(self.style.ERROR("   - No teachers found"))
            if not classes:
                self.stdout.write(self.style.ERROR("   - No classes found"))
            return

        records_created = 0
        days_processed = 0
        
        for days_ago in range(1, days_back + 1):
            date = timezone.now().date() - timedelta(days=days_ago)
            
            # Skip weekends (optional)
            if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                self.stdout.write(f"⏭️  Skipping weekend date: {date}")
                continue

            days_processed += 1
            self.stdout.write(f"📅 Processing date: {date}")
            
            # Calculate how many students to sample (80%)
            sample_size = max(1, int(len(students) * 0.8))
            self.stdout.write(f"   Selecting {sample_size} students out of {len(students)}")
            
            selected_students = random.sample(students, k=sample_size)
            
            for student in selected_students:
                try:
                    # Debug the random choices
                    status_choices = [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.LATE, AttendanceStatus.EXCUSED]
                    selected_status = random.choices(
                        status_choices,
                        weights=[85, 8, 5, 2],
                        k=1
                    )[0]
                    
                    selected_class = random.choice(classes)
                    selected_teacher = random.choice(teachers)
                    
                    self.stdout.write(f"   Creating record for {student} - Status: {selected_status}")
                    
                    AttendanceRecord.objects.create(
                        student=student,
                        class_ref=selected_class,
                        date=date,
                        status=selected_status,
                        recorded_by=selected_teacher
                    )
                    records_created += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error creating attendance for {student}: {str(e)}"))
                    # Print full traceback for debugging
                    import traceback
                    self.stdout.write(self.style.ERROR(traceback.format_exc()))

        self.stdout.write(self.style.SUCCESS(f"✅ Created {records_created} attendance records over {days_processed} days!"))