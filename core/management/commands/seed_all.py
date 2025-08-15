from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Seed all apps in correct dependency order"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Base number of records to create per app'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        # Accounts must come first (creates users, classes, and subjects)
        call_command('seed', count=options['count'], clear=options['clear'])
        
        # Then assessment (needs subjects from accounts)
        call_command('seed_assessment', count=int(options['count']/2), clear=options['clear'])
        
        # Then announcements (depends on accounts)
        call_command('seed_announcements', count=options['count'], clear=options['clear'])
        
        # Then attendance (depends on accounts)
        call_command('seed_attendance', days=30, clear=options['clear'])
        
        # Finally events (depends on accounts)
        call_command('seed_events', count=options['count'], clear=options['clear'])
        
        self.stdout.write(self.style.SUCCESS("🌱 Successfully seeded ALL apps!"))
        
        
        
# rm db.sqlite3
# python manage.py makemigrations
# python manage.py migrate
# python manage.py seed_all --count 40 --clear