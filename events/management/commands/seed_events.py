from django.core.management.base import BaseCommand
from faker import Faker
from events.models import Event, EventParticipant
from accounts.models import StudentProfile, TeacherProfile, ParentProfile
import random
from django.utils import timezone
from datetime import timedelta

fake = Faker()

class Command(BaseCommand):
    help = "Seed school events with participants"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=15,
            help='Number of events to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all events before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            Event.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Cleared all events."))

        self.create_events_and_participants(options['count'])
        self.stdout.write(self.style.SUCCESS(f"✅ Created {options['count']} events with participants!"))

    def create_events_and_participants(self, count):
        students = list(StudentProfile.objects.all())
        teachers = list(TeacherProfile.objects.all())
        parents = list(ParentProfile.objects.all())

        event_types = [
            "Sports Day", "Science Fair", "Parent-Teacher Meeting",
            "Cultural Festival", "Graduation", "Field Trip",
            "Debate Competition", "Music Concert"
        ]

        for _ in range(count):
            # Create timezone-aware datetime
            future_date = fake.future_datetime(end_date="+90d")
            aware_date = timezone.make_aware(future_date)

            event = Event.objects.create(
                title=f"{random.choice(event_types)} {fake.city_suffix()}",
                description=fake.paragraph(nb_sentences=5),
                date=aware_date,
                location=fake.city() + " " + random.choice(["Auditorium", "Field", "Hall", "Gym"])
            )

            # Add participants (5-20 per event)
            for __ in range(random.randint(5, 20)):
                participant_type = random.choices(
                    ['student', 'teacher', 'parent'],
                    weights=[60, 20, 20],
                    k=1
                )[0]

                EventParticipant.objects.create(
                    event=event,
                    student=random.choice(students) if participant_type == 'student' else None,
                    teacher=random.choice(teachers) if participant_type == 'teacher' else None,
                    parent=random.choice(parents) if participant_type == 'parent' else None
                )