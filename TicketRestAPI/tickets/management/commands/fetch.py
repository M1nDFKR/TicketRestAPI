from django.core.management.base import BaseCommand
from tickets.utils import create_ticket_instances

class Command(BaseCommand):
    help = 'Fetches emails and creates tickets'

    def handle(self, *args, **options):
        create_ticket_instances()
        self.stdout.write(self.style.SUCCESS('Successfully fetched emails and processed tickets'))
