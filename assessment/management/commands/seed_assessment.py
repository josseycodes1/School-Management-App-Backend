from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from faker import Faker
from assessment.models import Grade, Exam, Assignment, Result
from accounts.models import Subject, StudentProfile, TeacherProfile
import random

fake = Faker()

class Command(BaseCommand):
    help = "Seed assessment data (grades, exams, assignments, results)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of exams/assignments to create per subject'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all assessment data before seeding'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Starting assessment seeding...")
        
        if not Subject.objects.exists():
            self.stdout.write(self.style.ERROR("❌ No subjects found. Run accounts seed first!"))
            return

        if options['clear']:
            self.stdout.write("🧹 Clearing assessment data...")
            try:
                Result.objects.all().delete()
                Exam.objects.all().delete()
                Assignment.objects.all().delete()
                Grade.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("✅ Cleared all assessment data."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error clearing data: {e}"))
                return

        self.create_grades()
        self.create_exams_and_assignments(options['count'])
        self.create_results()
        self.stdout.write(self.style.SUCCESS(f"✅ Created assessment data!"))

    def create_grades(self):
        self.stdout.write("📊 Creating grade levels...")
        try:
           
            if Grade.objects.exists():
                self.stdout.write("📊 Grade levels already exist, skipping...")
                return
                
            grades = [
                ("A", "Excellent"),
                ("B", "Good"),
                ("C", "Average"),
                ("D", "Below Average"),
                ("F", "Fail")
            ]
            
            created_count = 0
            for name, desc in grades:
                Grade.objects.create(name=name, description=desc)
                created_count += 1
                self.stdout.write(f"   Created grade: {name} - {desc}")
                
            self.stdout.write(self.style.SUCCESS(f"📊 Created {created_count} grade levels"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating grades: {e}"))
            
            raise

    def create_exams_and_assignments(self, count_per_subject):
        self.stdout.write("📝 Creating exams and assignments...")
        
        subjects = list(Subject.objects.all())
        teachers = list(TeacherProfile.objects.all())
        grades = list(Grade.objects.all())
        
        self.stdout.write(f"   Found {len(subjects)} subjects, {len(teachers)} teachers, {len(grades)} grades")

        exams_created = 0
        assignments_created = 0

        for subject in subjects:
            self.stdout.write(f"   Processing subject: {subject.name}")
            
           
            for i in range(count_per_subject):
                try:
                    exam_date = timezone.make_aware(fake.future_datetime(end_date="+60d"))
                    Exam.objects.create(
                        title=f"{subject.name} {fake.word().title()} Exam",
                        subject=subject,
                        teacher=random.choice(teachers),
                        grade=random.choice(grades),
                        exam_date=exam_date
                    )
                    exams_created += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error creating exam for {subject.name}: {e}"))

            
            for i in range(count_per_subject):
                try:
                    due_date = timezone.make_aware(fake.future_datetime(end_date="+30d"))
                    Assignment.objects.create(
                        title=f"{subject.name} {fake.word().title()} Assignment",
                        description=fake.paragraph(),
                        subject=subject,
                        teacher=random.choice(teachers),
                        grade=random.choice(grades),
                        due_date=due_date
                    )
                    assignments_created += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error creating assignment for {subject.name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"📝 Created {exams_created} exams & {assignments_created} assignments"))

    def create_results(self):
        self.stdout.write("🎯 Creating student results...")
        
        students = list(StudentProfile.objects.all())
        exams = list(Exam.objects.all())
        assignments = list(Assignment.objects.all())
        
        self.stdout.write(f"   Found {len(students)} students, {len(exams)} exams, {len(assignments)} assignments")

        results_created = 0

       
        for exam in exams:
            try:
                
                sample_size = min(5, len(students))
                for student in random.sample(students, k=sample_size):
                    Result.objects.create(
                        student=student,
                        exam=exam,
                        score=random.uniform(60, 100)
                    )
                    results_created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating results for exam {exam.title}: {e}"))

        
        for assignment in assignments:
            try:
                
                sample_size = min(5, len(students))
                for student in random.sample(students, k=sample_size):
                    Result.objects.create(
                        student=student,
                        assignment=assignment,
                        score=random.uniform(50, 100)
                    )
                    results_created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating results for assignment {assignment.title}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"🎯 Created {results_created} student results"))