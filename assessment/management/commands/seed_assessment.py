from django.core.management.base import BaseCommand
from django.utils import timezone
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
        # Clear data if requested
        if options['clear']:
            Result.objects.all().delete()
            Exam.objects.all().delete()
            Assignment.objects.all().delete()
            Grade.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Cleared all assessment data."))

        # Step 1: Create grades
        self.create_grades()

        # Step 2: Create exams and assignments
        self.create_exams_and_assignments(options['count'])

        # Step 3: Create results
        self.create_results()

        self.stdout.write(self.style.SUCCESS("🌱 Successfully seeded assessment data!"))

    def create_grades(self):
        if Grade.objects.exists():
            self.stdout.write("📊 Grades already exist, skipping creation.")
            return

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
        subjects = list(Subject.objects.all())
        teachers = list(TeacherProfile.objects.all())
        grades = list(Grade.objects.all())

        if not subjects:
            self.stdout.write(self.style.ERROR("❌ No subjects found. Seed accounts first!"))
            return
        if not teachers:
            self.stdout.write(self.style.ERROR("❌ No teachers found. Seed accounts first!"))
            return
        if not grades:
            self.stdout.write(self.style.ERROR("❌ No grades found. Seed assessment first!"))
            return

        for subject in subjects:
            # Exams
            for _ in range(count_per_subject):
                Exam.objects.create(
                    title=f"{subject.name} {fake.word().title()} Exam",
                    subject=subject,
                    teacher=random.choice(teachers),
                    grade=random.choice(grades),
                    exam_date=fake.future_date(end_date="+60d")
                )

            # Assignments
            for _ in range(count_per_subject):
                Assignment.objects.create(
                    title=f"{subject.name} {fake.word().title()} Assignment",
                    description=fake.paragraph(),
                    subject=subject,
                    teacher=random.choice(teachers),
                    grade=random.choice(grades),
                    due_date=fake.future_date(end_date="+30d")
                )

        self.stdout.write(self.style.SUCCESS(f"📝 Created {count_per_subject} exams & assignments per subject"))

    def create_results(self):
        students = list(StudentProfile.objects.all())
        exams = list(Exam.objects.all())
        assignments = list(Assignment.objects.all())

        if not students:
            self.stdout.write(self.style.WARNING("⚠️ No students found. Skipping results creation."))
            return
        if not exams and not assignments:
            self.stdout.write(self.style.WARNING("⚠️ No exams or assignments found. Skipping results creation."))
            return

        # Exam results
        for exam in exams:
            participant_count = max(1, int(len(students) * 0.9))
            for student in random.sample(students, k=participant_count):
                Result.objects.create(
                    student=student,
                    exam=exam,
                    score=random.uniform(60, 100)
                )

        # Assignment results
        for assignment in assignments:
            participant_count = max(1, int(len(students) * 0.8))
            for student in random.sample(students, k=participant_count):
                Result.objects.create(
                    student=student,
                    assignment=assignment,
                    score=random.uniform(50, 100)
                )

        self.stdout.write(self.style.SUCCESS("🎯 Created realistic student results"))
