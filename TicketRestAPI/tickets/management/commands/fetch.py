from django.core.management.base import BaseCommand
from tickets.utils import fetch_and_process_emails

class Command(BaseCommand):
    help = 'Fetches emails and creates tickets'

    def handle(self, *args, **options):
        fetch_and_process_emails()
        self.stdout.write(self.style.SUCCESS('Successfully fetched emails and processed tickets'))
