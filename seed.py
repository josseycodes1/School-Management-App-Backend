import os
import django
import random
from datetime import date, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from accounts.models import User, AdminProfile, StudentProfile, TeacherProfile, ParentProfile

def seed_accounts():
    print("\n👥 SEEDING ACCOUNTS...")

    users = []

    # Create superuser
    superuser = User.objects.create_superuser(
        email="admin@school.com",
        first_name="Admin",
        last_name="User",
        role="admin",
        password="admin123"
    )
    users.append(superuser)
    print("✔️ Superuser created")

    # Create 5 teachers
    for i in range(1, 6):
        teacher = User.objects.create(
            email=f"teacher{i}@school.com",
            first_name=f"Teacher{i}",
            last_name="Educator",
            role="teacher",
            password=make_password("teacher123")
        )
        TeacherProfile.objects.create(user=teacher)
        users.append(teacher)
    print("✔️ 5 Teachers created")

    # Create 10 students with parents
    students = []
    for i in range(1, 11):
        # Create parent (User + ParentProfile)
        parent = User.objects.create(
            email=f"parent{i}@family.com",
            first_name=f"Parent{i}",
            last_name=f"Family",
            role="parent",
            password=make_password("parent123")
        )
        ParentProfile.objects.create(user=parent)

        # Create student (User + StudentProfile)
        student = User.objects.create(
            email=f"student{i}@school.com",
            first_name=f"Student{i}",
            last_name="Family",
            role="student",
            password=make_password("student123")
        )
        StudentProfile.objects.create(
            user=student,
            parent=parent,  # ✅ FIXED: assign the User, not the ParentProfile
            admission_number=f"STD{100+i}",
            birth_date=date.today() - timedelta(days=365 * random.randint(10, 15))
        )
        students.append(student)
        users.append(student)
        users.append(parent)
    print("✔️ 10 Students and Parents created")

    return users

def seed_all():
    print("\n🏫 STARTING SCHOOL DATABASE SEEDING 🏫")
    users = seed_accounts()
    print("\n✅ SEEDING COMPLETE!\n")

if __name__ == "__main__":
    seed_all()
