import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import (
    User, AdminProfile, TeacherProfile, ParentProfile, StudentProfile,
    Classes, Subject, AcademicYear, Gender, UserRole
)
from faker import Faker
from django.utils import timezone

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with dummy accounts data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of each user type to create (default: 20)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing data before seeding',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        if clear:
            self.clear_data()
            self.stdout.write(self.style.SUCCESS("✅ Cleared all accounts data."))

        self.create_superuser()
        self.create_academic_years()
        self.create_classes()
        self.create_subjects()  
        self.create_teachers(count)
        self.create_parents(count)
        self.create_students(count)
        self.stdout.write(self.style.SUCCESS(f"✅ Successfully seeded {count} users per role!"))

    def clear_data(self):
        User.objects.all().delete()
        Classes.objects.all().delete()
        AcademicYear.objects.all().delete()
        Subject.objects.all().delete() 

    def create_superuser(self):
        if not User.objects.filter(role=UserRole.ADMIN).exists():
            User.objects.create_superuser(
                email="admin@school.com",
                password="admin123",
                first_name="Admin",
                last_name="User",
                role=UserRole.ADMIN
            )
            self.stdout.write(self.style.SUCCESS("👑 Created superuser: admin@school.com"))

    def create_academic_years(self):
        if not AcademicYear.objects.exists():
            AcademicYear.objects.create(name="2023/2024", current=False)
            AcademicYear.objects.create(name="2024/2025", current=True)
            self.stdout.write(self.style.SUCCESS("📅 Created academic years"))

    def create_classes(self):
        if not Classes.objects.exists():
            class_names = ["Primary 1", "Primary 2", "JSS 1", "JSS 2", "SSS 1"]
            for name in class_names:
                Classes.objects.create(name=name)
            self.stdout.write(self.style.SUCCESS("🏫 Created classes"))

    def create_subjects(self):
        if not Subject.objects.exists():
            classes = Classes.objects.all()
            subjects = ["Mathematics", "English", "Science", "History", "Geography"]
            
            for class_obj in classes:
                for subject_name in subjects:
                    Subject.objects.create(
                        name=f"{subject_name} {class_obj.name}",
                        assigned_class=class_obj
                    )
            self.stdout.write(self.style.SUCCESS("📚 Created subjects for all classes"))

    def create_teachers(self, count):
        existing = User.objects.filter(role=UserRole.TEACHER).count()
        needed = max(0, count - existing)
        
        for _ in range(needed):
            user = User.objects.create_user(
                email=fake.unique.email(),
                password="teacher123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=UserRole.TEACHER,
                is_active=True,
                is_verified=True
            )
            TeacherProfile.objects.create(
                user=user,
                phone=fake.phone_number()[:15],
                address=fake.address(),
                gender=random.choice([g[0] for g in Gender.choices]),
                subject_specialization=fake.job(),
                hire_date=fake.date_between(start_date="-5y", end_date="today"),
                qualifications=", ".join(fake.words(nb=3)),
                is_principal=random.random() > 0.9
            )
        self.stdout.write(self.style.SUCCESS(f"👩‍🏫 Created {needed} new teachers (Total: {count})"))

    def create_parents(self, count):
        existing = User.objects.filter(role=UserRole.PARENT).count()
        needed = max(0, count - existing)
        
        for _ in range(needed):
            user = User.objects.create_user(
                email=fake.unique.email(),
                password="parent123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=UserRole.PARENT,
                is_active=True,
                is_verified=True
            )
            ParentProfile.objects.create(
                user=user,
                phone=fake.phone_number()[:15],
                address=fake.address(),
                gender=random.choice([g[0] for g in Gender.choices]),
                emergency_contact=fake.phone_number()[:15],
                occupation=fake.job()
            )
        self.stdout.write(self.style.SUCCESS(f"👪 Created {needed} new parents (Total: {count})"))

    def create_students(self, count):
        existing = User.objects.filter(role=UserRole.STUDENT).count()
        needed = max(0, count - existing)
        classes = list(Classes.objects.all())
        academic_year = AcademicYear.objects.get(current=True)

        for _ in range(needed):
            user = User.objects.create_user(
                email=fake.unique.email(),
                password="student123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=UserRole.STUDENT,
                is_active=True,
                is_verified=True
            )
            StudentProfile.objects.create(
                user=user,
                phone=fake.phone_number()[:15],
                address=fake.address(),
                gender=random.choice([g[0] for g in Gender.choices]),
                admission_number=f"STD-{fake.unique.random_number(digits=5)}",
                class_level=random.choice(classes).name,
                academic_year=academic_year.name,
                parent_name=fake.name(),
                parent_contact=fake.phone_number()[:15],
                medical_notes=fake.sentence() if random.random() > 0.7 else "",
                is_onboarded=random.random() > 0.3
            )
        self.stdout.write(self.style.SUCCESS(f"🎓 Created {needed} new students (Total: {count})"))