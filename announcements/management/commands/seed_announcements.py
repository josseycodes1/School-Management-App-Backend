from django.core.management.base import BaseCommand
from faker import Faker
from announcements.models import Announcement, AnnouncementAudience
from accounts.models import StudentProfile, TeacherProfile, ParentProfile
import random
from django.utils import timezone
from datetime import timedelta
import pytz  

fake = Faker()

class Command(BaseCommand):
    help = "Seed dummy announcements with proper audience targeting"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of announcements to create (default: 20)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing announcements before seeding',
        )

    def handle(self, *args, **options):
      
        required_models = [StudentProfile, TeacherProfile, ParentProfile]
        for model in required_models:
            if not model.objects.exists():
                self.stdout.write(self.style.ERROR(f"❌ No {model.__name__} found. Run accounts seed first!"))
                return

        if options['clear']:
            Announcement.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Cleared all announcements."))

        self.create_announcements(options['count'])
        self.stdout.write(self.style.SUCCESS(f"✅ Created {options['count']} announcements with audiences!"))

    def create_announcements(self, count):
        students = list(StudentProfile.objects.all())
        teachers = list(TeacherProfile.objects.all())
        parents = list(ParentProfile.objects.all())

        for _ in range(count):
            
            end_date = None
            if random.random() > 0.3:
                end_date = fake.future_datetime(end_date="+30d")
                end_date = timezone.make_aware(end_date, timezone.get_current_timezone())

            announcement = Announcement.objects.create(
                title=fake.sentence(nb_words=6),
                message=fake.paragraph(nb_sentences=5),
                start_date=timezone.now(),
                end_date=end_date,
                is_active=random.random() > 0.2
            )

          
            for __ in range(random.randint(1, 3)):
                audience_type = random.choices(
                    ['student', 'teacher', 'parent'],
                    weights=[60, 20, 20],  
                    k=1
                )[0]
                
                audience = AnnouncementAudience(
                    announcement=announcement,
                    student=random.choice(students) if audience_type == 'student' else None,
                    teacher=random.choice(teachers) if audience_type == 'teacher' else None,
                    parent=random.choice(parents) if audience_type == 'parent' else None
                )
                audience.save()