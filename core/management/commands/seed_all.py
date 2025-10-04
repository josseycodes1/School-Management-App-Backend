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
        # 1. Accounts (base data)
        call_command('seed', count=options['count'], clear=options['clear'])
        
        # 2. Assessment (needs subjects and students)
        call_command('seed_assessment', count=int(options['count']/2), clear=options['clear'])
        
        # 3. Attendance (needs students and classes)
        call_command('seed_attendance', days=30, clear=options['clear'])
        
        # 4. Announcements (needs all user types)
        call_command('seed_announcements', count=options['count'], clear=options['clear'])
        
        # 5. Events (needs all user types)
        call_command('seed_events', count=options['count'], clear=options['clear'])
        
        
        
# rm db.sqlite3
# python manage.py makemigrations
# python manage.py migrate
# python manage.py seed_all --count 40 --clear

# python manage.py seed --count 20 --clear
# python manage.py seed_assessment --count 10 --clear
# python manage.py seed_announcements --count 20 --clear
# python manage.py seed_attendance --days 30 --clear
# python manage.py seed_events --count 20 --clear