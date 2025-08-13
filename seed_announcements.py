import random
from datetime import timedelta
from django.utils import timezone

from announcements.models import Announcement, AnnouncementAudience
from accounts.models import StudentProfile, TeacherProfile, ParentProfile

# --- Create sample announcements ---
titles = [
    "School Will Be Closed on Monday",
    "New Library Books Available",
    "Parent-Teacher Meeting This Friday",
    "Sports Day Scheduled for Next Month",
    "Reminder: Submit Homework by Wednesday"
]

messages = [
    "Due to a public holiday, classes will not be held on Monday. Please plan accordingly.",
    "The library has received a new collection of books. All students are encouraged to visit.",
    "We will be holding our regular parent-teacher meeting this Friday at 3 PM in the main hall.",
    "Get ready for our annual sports day! Details will be shared soon.",
    "All students must submit their homework by Wednesday to avoid penalties."
]

now = timezone.now()

announcements = []
for i in range(5):
    ann = Announcement.objects.create(
        title=titles[i],
        message=messages[i],
        start_date=now - timedelta(days=random.randint(0, 3)),
        end_date=now + timedelta(days=random.randint(3, 10)),
        is_active=True
    )
    announcements.append(ann)

print(f"✅ Created {len(announcements)} announcements.")

# --- Assign random audiences ---
students = list(StudentProfile.objects.all())
teachers = list(TeacherProfile.objects.all())
parents = list(ParentProfile.objects.all())

for ann in announcements:
    # Randomly assign between 1 and 3 audience members
    for _ in range(random.randint(1, 3)):
        role_choice = random.choice(["student", "teacher", "parent"])
        if role_choice == "student" and students:
            AnnouncementAudience.objects.create(
                announcement=ann,
                student=random.choice(students)
            )
        elif role_choice == "teacher" and teachers:
            AnnouncementAudience.objects.create(
                announcement=ann,
                teacher=random.choice(teachers)
            )
        elif role_choice == "parent" and parents:
            AnnouncementAudience.objects.create(
                announcement=ann,
                parent=random.choice(parents)
            )

print("✅ Assigned audiences to announcements.")
