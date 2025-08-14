import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event

class Command(BaseCommand):
    help = "Seeds the database with sample events"

    def handle(self, *args, **kwargs):
        Event.objects.all().delete()  # Optional: Clear old events before seeding

        titles = [
            "Parent-Teacher Conference", "Science Fair", "Sports Day", "Music Recital",
            "School Anniversary", "Art Exhibition", "Debate Competition", "Drama Night",
            "Math Olympiad", "Graduation Ceremony", "Career Day", "Field Trip",
            "Book Fair", "Coding Hackathon", "Health Awareness Week", "Cultural Day",
            "Speech Contest", "Environmental Cleanup", "Leadership Summit", "Quiz Competition"
        ]
        locations = [
            "School Hall", "Auditorium", "Sports Field", "Library",
            "Computer Lab", "Art Room", "Conference Room", "Music Room"
        ]

        for title in titles:
            Event.objects.create(
                title=title,
                description=f"This is a description for {title}.",
                date=timezone.now() + timedelta(days=random.randint(-30, 60)),
                location=random.choice(locations)
            )

        self.stdout.write(self.style.SUCCESS("✅ Successfully seeded 20 events."))
