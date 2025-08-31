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
        grades = list(Grade.objects.all())

        for subject in subjects:
            # Create exams
            for _ in range(count_per_subject):
                try:
                    exam_date = timezone.make_aware(fake.future_datetime(end_date="+60d"))
                    Exam.objects.create(
                        title=f"{subject.name} {fake.word().title()} Exam",
                        subject=subject,
                        teacher=random.choice(teachers),
                        grade=random.choice(grades),
                        exam_date=exam_date
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error creating exam for {subject.name}: {e}"))

            # Create assignments
            for _ in range(count_per_subject):
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
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error creating assignment for {subject.name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"📝 Created {count_per_subject} exams & assignments per subject"))

    def create_results(self):
        students = list(StudentProfile.objects.all())
        exams = list(Exam.objects.all())
        assignments = list(Assignment.objects.all())

        for exam in exams:
            try:
                for student in random.sample(students, k=int(len(students)*0.9)):
                    Result.objects.create(
                        student=student,
                        exam=exam,
                        score=random.uniform(60, 100)
                    )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating results for exam {exam.title}: {e}"))

        for assignment in assignments:
            try:
                for student in random.sample(students, k=int(len(students)*0.8)):
                    Result.objects.create(
                        student=student,
                        assignment=assignment,
                        score=random.uniform(50, 100)
                    )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating results for assignment {assignment.title}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎯 Created realistic student results"))
