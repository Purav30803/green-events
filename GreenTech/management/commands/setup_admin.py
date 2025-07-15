from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Set up admin user and initial data for GreenTech admin panel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@greentech.com',
            help='Admin email (default: admin@greentech.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Admin password (default: admin123)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Create superuser if it doesn't exist
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user:\n'
                    f'Username: {username}\n'
                    f'Email: {email}\n'
                    f'Password: {password}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists.')
            )

        # Create regular admin user for GreenTech
        greentech_admin, created = User.objects.get_or_create(
            username='greentech_admin',
            defaults={
                'email': 'greentech@admin.com',
                'first_name': 'GreenTech',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
                'password': make_password('greentech123')
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created GreenTech admin user:\n'
                    f'Username: greentech_admin\n'
                    f'Password: greentech123'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('GreenTech admin user already exists.')
            )

        self.stdout.write(
            self.style.SUCCESS(
                '\nAdmin panel setup complete!\n'
                'You can now access:\n'
                '- Main Django admin: /admin/\n'
                '- GreenTech admin: /greentech-admin/\n'
                '\nTo create sample events, run:\n'
                'python manage.py create_sample_events'
            )
        ) 