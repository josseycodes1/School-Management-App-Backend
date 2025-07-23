import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import models
from accounts.models import User, UserRole, AdminProfile, ParentProfile, TeacherProfile, StudentProfile
from academics.models import Subject, Classes, Lesson
from assessment.models import Assignment, Exam, Result, Grade
from attendance.models import AttendanceRecord, AttendanceStatus
from events.models import Event, EventParticipant
from announcement.models import Announcement, AnnouncementAudience

# Sample names
first_names = ["Jane", "John", "Alice", "Bob", "Grace", "Daniel", "Linda", "Charles", "Mary", "James"]
last_names = ["Doe", "Smith", "Johnson", "Lee", "Brown", "Davis", "Wilson", "Clark", "Taylor", "Moore"]

# Create user and appropriate profile
def create_user(email, first_name, last_name, role, password="test1234", **profile_fields):
    user = User.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        password=password
    )

    if role == UserRole.ADMIN:
        AdminProfile.objects.create(user=user, **profile_fields)
    elif role == UserRole.PARENT:
        ParentProfile.objects.create(user=user, **profile_fields)
    elif role == UserRole.TEACHER:
        TeacherProfile.objects.create(
            user=user,
            subject_specialization=random.choice(["Math", "English", "Biology"]),
            hire_date=timezone.now() - timedelta(days=100),
            **profile_fields
        )
    elif role == UserRole.STUDENT:
        parent = random.choice(ParentProfile.objects.all())
        StudentProfile.objects.create(
            user=user,
            parent=parent.user,
            admission_number=f"ADM{random.randint(10000, 99999)}",
            **profile_fields
        )
    return user

# Main seeding function
def run():
    print("🧹 Clearing old data...")
    User.objects.all().delete()
    Subject.objects.all().delete()
    Classes.objects.all().delete()
    Lesson.objects.all().delete()
    Grade.objects.all().delete()
    Assignment.objects.all().delete()
    Exam.objects.all().delete()
    Result.objects.all().delete()
    AttendanceRecord.objects.all().delete()
    Event.objects.all().delete()
    Announcement.objects.all().delete()

    print("👤 Creating users and profiles...")
    admins = [create_user(f"admin{i}@example.com", f"Admin{i}", "User", UserRole.ADMIN) for i in range(1, 3)]
    parents = [create_user(f"parent{i}@example.com", f"Parent{i}", random.choice(last_names), UserRole.PARENT) for i in range(1, 5)]
    teachers = [create_user(f"teacher{i}@example.com", f"Teacher{i}", random.choice(last_names), UserRole.TEACHER) for i in range(1, 4)]

    print("👶 Creating students...")
    students = [
        create_user(
            f"student{i}@example.com",
            random.choice(first_names),
            random.choice(last_names),
            UserRole.STUDENT
        )
        for i in range(1, 11)
    ]

    print("🏫 Creating classes and subjects...")
    classes = []
    for i in range(1, 4):
        class_name = f"Class {chr(64+i)}"
        teacher = random.choice(TeacherProfile.objects.all())
        classes.append(Classes.objects.create(name=class_name, teacher=teacher))

    subjects = []
    subject_names = ["Mathematics", "English"]
    for name in subject_names:
        assigned_class = random.choice(classes)
        teacher = random.choice(TeacherProfile.objects.all())
        subject = Subject.objects.create(name=name, assigned_class=assigned_class, teacher=teacher)
        subjects.append(subject)

    print("🎓 Creating grades...")
    grades = []
    for i in range(1, 4):
        grade = Grade.objects.create(name=f"Grade {i}", description="Academic level")
        grades.append(grade)

    print("📘 Creating lessons...")
    for subject in subjects:
        for i in range(1, 3):
            Lesson.objects.create(
                title=f"{subject.name} - Lesson {i}",
                subject=subject,
                content="This is a sample lesson content.",
                date=timezone.now().date()
            )

    print("📝 Creating assignments...")
    for i in range(5):
        Assignment.objects.create(
            title=f"Assignment {i+1}",
            description="Complete your exercises.",
            subject=random.choice(subjects),
            teacher=random.choice(TeacherProfile.objects.all()),
            grade=random.choice(grades),
            due_date=timezone.now() + timedelta(days=random.randint(3, 10))
        )

    print("🧪 Creating exams and results...")
    exams = [
        Exam.objects.create(
            title=f"Exam {i+1}",
            subject=random.choice(subjects),
            teacher=random.choice(TeacherProfile.objects.all()),
            grade=random.choice(grades),
            exam_date=timezone.now().date() + timedelta(days=random.randint(5, 15))
        )
        for i in range(2)
    ]

    for student in StudentProfile.objects.all():
        for exam in exams:
            Result.objects.create(
                student=student,
                exam=exam,
                score=random.uniform(60, 100)
            )

    print("🧍 Creating attendance records...")
    for student in StudentProfile.objects.all():
        AttendanceRecord.objects.create(
            student=student,
            class_ref=random.choice(classes),
            date=timezone.now().date(),
            status=random.choice(AttendanceStatus.choices)[0],
            recorded_by=random.choice(TeacherProfile.objects.all())
        )

    print("📅 Creating events and participants...")
    for i in range(2):
        event = Event.objects.create(
            title=f"Event {i+1}",
            description="Annual event",
            date=timezone.now() + timedelta(days=3+i),
            location="School Auditorium"
        )

        for s in random.sample(list(StudentProfile.objects.all()), 3):
            EventParticipant.objects.create(event=event, student=s)
        for t in random.sample(list(TeacherProfile.objects.all()), 1):
            EventParticipant.objects.create(event=event, teacher=t)
        for p in random.sample(list(ParentProfile.objects.all()), 1):
            EventParticipant.objects.create(event=event, parent=p)

    print("📣 Creating announcements and audiences...")
    for i in range(2):
        ann = Announcement.objects.create(
            title=f"Announcement {i+1}",
            message="Important school update.",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=5),
            is_active=True
        )
        AnnouncementAudience.objects.create(announcement=ann, student=random.choice(StudentProfile.objects.all()))
        AnnouncementAudience.objects.create(announcement=ann, teacher=random.choice(TeacherProfile.objects.all()))
        AnnouncementAudience.objects.create(announcement=ann, parent=random.choice(ParentProfile.objects.all()))

    print("✅ Done! Seeded records successfully.")

# Run script
if __name__ == "__main__":
    run()
