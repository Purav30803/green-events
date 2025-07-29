from django.core.management.base import BaseCommand
from GreenTech.models import VisitorCount


class Command(BaseCommand):
    help = 'Initialize visitor count'

    def handle(self, *args, **options):
        visitor_count = VisitorCount.get_or_create_singleton()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized visitor count: {visitor_count.total_visitors}'
            )
        ) 