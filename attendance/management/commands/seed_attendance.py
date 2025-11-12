from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from attendance.models import AttendanceRecord, AttendanceStatus
from accounts.models import StudentProfile, TeacherProfile, Classes
import random
from datetime import timedelta, datetime

fake = Faker()

class Command(BaseCommand):
    help = "Seed attendance records for students"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all attendance records before seeding'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to generate attendance for (default: 30)'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            default=None,
            help='Start date for attendance records (format: YYYY-MM-DD)'
        )

    def handle(self, *args, **options):
        
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

        # Use current date for seeding
        if options['start_date']:
            start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
        else:
            # Start from today or a recent date
            start_date = datetime.now().date() - timedelta(days=7)  # Include some past week + future
        
        end_date = start_date + timedelta(days=options['days'])
        
        self.stdout.write(f"📅 Generating attendance from {start_date} to {end_date} ({options['days']} days)")
        
        self.create_attendance_records(start_date, end_date)
        self.stdout.write(self.style.SUCCESS(f"✅ Completed attendance seeding from {start_date} to {end_date}!"))

    def create_attendance_records(self, start_date, end_date):
        students = list(StudentProfile.objects.all())
        teachers = list(TeacherProfile.objects.all())
        classes = list(Classes.objects.all())
        
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
        
        # Calculate the date range
        current_date = start_date
        date_range = []
        
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        self.stdout.write(f"🗓️  Generating attendance for {len(date_range)} days from {start_date} to {end_date}")
        
        for date in date_range:
            # Skip weekends (Saturday=5, Sunday=6)
            if date.weekday() >= 5:
                self.stdout.write(f"⏭️  Skipping weekend date: {date}")
                continue

            days_processed += 1
            self.stdout.write(f"📅 Processing date: {date}")
            
            # Select 80% of students for each day
            sample_size = max(1, int(len(students) * 0.8))
            self.stdout.write(f"   Selecting {sample_size} students out of {len(students)}")
            
            selected_students = random.sample(students, k=sample_size)
            
            for student in selected_students:
                try:
                    # Weighted random selection for attendance status
                    status_choices = [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.LATE, AttendanceStatus.EXCUSED]
                    selected_status = random.choices(
                        status_choices,
                        weights=[85, 8, 5, 2],  # 85% present, 8% absent, 5% late, 2% excused
                        k=1
                    )[0]
                    
                    selected_class = random.choice(classes)
                    selected_teacher = random.choice(teachers)
                    
                    # Only show detailed logging for recent dates to reduce noise
                    if date >= datetime.now().date() - timedelta(days=7):
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
                    
                    import traceback
                    self.stdout.write(self.style.ERROR(traceback.format_exc()))

        self.stdout.write(self.style.SUCCESS(f"✅ Created {records_created} attendance records over {days_processed} days from {start_date} to {end_date}!"))