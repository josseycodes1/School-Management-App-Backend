from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from assessment.models import Grade, Exam, Assignment, Result
from accounts.models import Subject, StudentProfile, TeacherProfile, Classes
import random
from datetime import timedelta

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
        if not Subject.objects.exists():
            self.stdout.write(self.style.ERROR("❌ No subjects found. Run accounts seed first!"))
            return

        if options['clear']:
            Result.objects.all().delete()
            Exam.objects.all().delete()
            Assignment.objects.all().delete()
            Grade.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Cleared all assessment data."))

        self.create_grades()
        self.create_exams_and_assignments(options['count'])
        self.create_results()
        self.stdout.write(self.style.SUCCESS(f"✅ Created {options['count']} assessments per subject with results!"))

    def create_grades(self):
        if not Grade.objects.exists():
            grades = [
                ("A", "Excellent"),
                ("B", "Good"),
                ("C", "Average"),
                ("D", "Below Average"),
                ("F", "Fail")
            ]
            for name, desc in grades:
                Grade.objects.create(name=name, description=desc)
            self.stdout.write(self.style.SUCCESS("📊 Created grade levels"))

    def create_exams_and_assignments(self, count_per_subject):
        subjects = Subject.objects.all()
        teachers = list(TeacherProfile.objects.all())
        
        for subject in subjects:
            # Create exams
            for _ in range(count_per_subject):
                Exam.objects.create(
                    title=f"{subject.name} {fake.word().title()} Exam",
                    subject=subject,
                    teacher=random.choice(teachers),
                    grade=random.choice(Grade.objects.all()),
                    exam_date=fake.future_date(end_date="+60d")
                )
            
            # Create assignments
            for _ in range(count_per_subject):
                Assignment.objects.create(
                    title=f"{subject.name} {fake.word().title()} Assignment",
                    description=fake.paragraph(),
                    subject=subject,
                    teacher=random.choice(teachers),
                    grade=random.choice(Grade.objects.all()),
                    due_date=fake.future_date(end_date="+30d")
                )
        self.stdout.write(self.style.SUCCESS(f"📝 Created {count_per_subject} exams & assignments per subject"))

    def create_results(self):
        students = list(StudentProfile.objects.all())
        exams = list(Exam.objects.all())
        assignments = list(Assignment.objects.all())

        # Create exam results
        for exam in exams:
            for student in random.sample(students, k=int(len(students)*0.9)):  # 90% participation
                Result.objects.create(
                    student=student,
                    exam=exam,
                    score=random.uniform(60, 100)  # Scores between 60-100
                )

        # Create assignment results
        for assignment in assignments:
            for student in random.sample(students, k=int(len(students)*0.8)):  # 80% completion
                Result.objects.create(
                    student=student,
                    assignment=assignment,
                    score=random.uniform(50, 100)  # Scores between 50-100
                )
        self.stdout.write(self.style.SUCCESS("🎯 Created realistic student results"))