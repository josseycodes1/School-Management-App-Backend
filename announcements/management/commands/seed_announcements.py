from django.core.management.base import BaseCommand
from faker import Faker
from announcements.models import Announcement
from accounts.models import StudentProfile, TeacherProfile, ParentProfile
import random
from django.utils import timezone
from datetime import timedelta
import logging


logging.getLogger('faker').setLevel(logging.ERROR)

fake = Faker()

class Command(BaseCommand):
    help = "Seed dummy announcements with role-based audience targeting"

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
                self.stdout.write(self.style.WARNING(f"⚠️ No {model.__name__} found. Announcements will still be created with role-based targeting."))

        if options['clear']:
            deleted_count, _ = Announcement.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"✅ Cleared {deleted_count} announcements."))

        created_count = self.create_announcements(options['count'])
        self.stdout.write(self.style.SUCCESS(f"✅ Created {created_count} announcements with role-based audience targeting!"))

    def create_announcements(self, count):
      
        audience_combinations = [
           
            {'target_students': True, 'target_teachers': False, 'target_parents': False},
           
            {'target_students': False, 'target_teachers': True, 'target_parents': False},
            
            {'target_students': False, 'target_teachers': False, 'target_parents': True},
            
            {'target_students': True, 'target_teachers': True, 'target_parents': False},
            
            {'target_students': True, 'target_teachers': False, 'target_parents': True},
            
            {'target_students': False, 'target_teachers': True, 'target_parents': True},
            
            {'target_students': True, 'target_teachers': True, 'target_parents': True},
        ]

       
        weights = [30, 15, 10, 15, 10, 5, 15]

        created_count = 0
        for i in range(count):
            try:
               
                audience_config = random.choices(audience_combinations, weights=weights, k=1)[0]
                
               
                if i < 5:  
                    start_date = self.get_naive_datetime(fake.past_datetime(start_date="-30d"))
                else:
                    if random.random() > 0.7:
                        start_date = self.get_naive_datetime(fake.future_datetime(end_date="+7d"))
                    else:
                        start_date = timezone.now()
                
               
                end_date = None
                if random.random() > 0.4:  
                    end_date = start_date + timedelta(days=random.randint(1, 60))
                
                
                announcement_type = random.choice([
                    'general', 'exam', 'holiday', 'event', 'urgent', 'academic'
                ])
                
                title, message = self.generate_announcement_content(announcement_type, audience_config)
                
                announcement = Announcement.objects.create(
                    title=title,
                    message=message,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=random.random() > 0.1,  
                    **audience_config
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f"📢 Created: '{announcement.title}' "
                    f"for {', '.join(announcement.target_roles) if announcement.target_roles else 'no one'}"
                ))
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to create announcement: {e}"))
                continue

        return created_count

    def get_naive_datetime(self, dt):
       
        if timezone.is_aware(dt):
            return timezone.make_naive(dt)
        return dt

    def generate_announcement_content(self, announcement_type, audience_config):
       
        
        if announcement_type == 'general':
            titles = [
                "Important School Update",
                "General Information Notice",
                "School-wide Announcement",
                "Important Notice for All"
            ]
        elif announcement_type == 'exam':
            titles = [
                "Upcoming Examination Schedule",
                "Exam Guidelines and Regulations",
                "Mid-term Examination Notice",
                "Final Exam Timetable Released"
            ]
        elif announcement_type == 'holiday':
            titles = [
                "School Holiday Announcement",
                "Break Period Notice",
                "Upcoming Holiday Schedule",
                "Vacation Notice"
            ]
        elif announcement_type == 'event':
            titles = [
                "School Event Invitation",
                "Upcoming Cultural Festival",
                "Sports Day Announcement",
                "Annual Function Details"
            ]
        elif announcement_type == 'urgent':
            titles = [
                "URGENT: Important Notice",
                "Immediate Attention Required",
                "Emergency School Closure",
                "Urgent Update"
            ]
        else: 
            titles = [
                "Academic Calendar Update",
                "Curriculum Changes Notice",
                "New Course Offerings",
                "Academic Progress Report"
            ]

        title = random.choice(titles)
        
       
        audience_roles = []
        if audience_config['target_students']:
            audience_roles.append('students')
        if audience_config['target_teachers']:
            audience_roles.append('teachers')
        if audience_config['target_parents']:
            audience_roles.append('parents')
        
        audience_text = ", ".join(audience_roles) if audience_roles else "all members"
        
        message_intros = [
            f"Dear {audience_text},\n\n",
            f"Attention {audience_text}:\n\n",
            f"To all {audience_text}:\n\n",
            f"Notice for {audience_text}:\n\n"
        ]
        
        message_content = fake.paragraph(nb_sentences=random.randint(3, 8))
        
        
        if audience_config['target_parents'] and not audience_config['target_students']:
            closings = [
                "\n\nThank you for your cooperation and support.",
                "\n\nWe appreciate your partnership in your child's education.",
                "\n\nPlease feel free to contact the school office with any questions."
            ]
        elif audience_config['target_teachers'] and not audience_config['target_students']:
            closings = [
                "\n\nPlease review this information carefully.",
                "\n\nYour attention to this matter is appreciated.",
                "\n\nKindly acknowledge receipt of this notice."
            ]
        else:
            closings = [
                "\n\nPlease take note of this important information.",
                "\n\nYour cooperation is appreciated.",
                "\n\nFor any queries, please contact the administration."
            ]
        
        message = random.choice(message_intros) + message_content + random.choice(closings)
        
        return title, message