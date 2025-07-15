from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from GreenTech.models import Event
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample events for demonstration'

    def handle(self, *args, **options):
        # Create a sample user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@greenevents.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Sample events data
        events_data = [
            {
                'title': 'Community Tree Planting Day',
                'description': 'Join us for a day of environmental stewardship as we plant native trees in our local park. This event will help improve air quality and provide habitat for local wildlife. All tools and materials will be provided. Please wear comfortable clothing and closed-toe shoes.',
                'event_type': 'tree_planting',
                'location': 'Central Park, Downtown',
                'latitude': 40.7589,
                'longitude': -73.9851,
                'date': date.today() + timedelta(days=7),
                'start_time': '09:00',
                'end_time': '14:00',
                'max_participants': 30,
            },
            {
                'title': 'Beach Cleanup Initiative',
                'description': 'Help keep our beaches clean and protect marine life. We\'ll be collecting litter and debris from the shoreline. This is a family-friendly event suitable for all ages. Gloves and bags will be provided.',
                'event_type': 'cleanup',
                'location': 'Sunset Beach',
                'latitude': 40.7589,
                'longitude': -73.9851,
                'date': date.today() + timedelta(days=14),
                'start_time': '08:00',
                'end_time': '12:00',
                'max_participants': 50,
            },
            {
                'title': 'Recycling Workshop',
                'description': 'Learn about proper recycling practices and how to reduce your environmental footprint. This educational workshop will cover composting, plastic recycling, and sustainable living tips.',
                'event_type': 'recycling',
                'location': 'Community Center',
                'latitude': 40.7589,
                'longitude': -73.9851,
                'date': date.today() + timedelta(days=21),
                'start_time': '10:00',
                'end_time': '12:00',
                'max_participants': 25,
            },
            {
                'title': 'Wildlife Conservation Talk',
                'description': 'Join local conservation experts for an informative session about protecting local wildlife and their habitats. Learn about endangered species in our area and how you can help.',
                'event_type': 'conservation',
                'location': 'Nature Center',
                'latitude': 40.7589,
                'longitude': -73.9851,
                'date': date.today() + timedelta(days=28),
                'start_time': '14:00',
                'end_time': '16:00',
                'max_participants': 40,
            },
            {
                'title': 'Environmental Education Day',
                'description': 'A comprehensive educational event covering various environmental topics including climate change, renewable energy, and sustainable practices. Perfect for students and adults interested in environmental science.',
                'event_type': 'education',
                'location': 'University Campus',
                'latitude': 40.7589,
                'longitude': -73.9851,
                'date': date.today() + timedelta(days=35),
                'start_time': '09:00',
                'end_time': '17:00',
                'max_participants': 60,
            },
            {
                'title': 'Urban Garden Maintenance',
                'description': 'Help maintain our community urban garden. Activities include weeding, watering, and harvesting fresh produce that will be donated to local food banks.',
                'event_type': 'other',
                'location': 'Community Garden',
                'latitude': 40.7589,
                'longitude': -73.9851,
                'date': date.today() + timedelta(days=42),
                'start_time': '08:00',
                'end_time': '11:00',
                'max_participants': 20,
            },
        ]

        created_count = 0
        for event_data in events_data:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults={
                    'description': event_data['description'],
                    'event_type': event_data['event_type'],
                    'location': event_data['location'],
                    'latitude': event_data['latitude'],
                    'longitude': event_data['longitude'],
                    'date': event_data['date'],
                    'start_time': event_data['start_time'],
                    'end_time': event_data['end_time'],
                    'max_participants': event_data['max_participants'],
                    'organizer': user,
                    'is_active': True,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample events')
        ) 