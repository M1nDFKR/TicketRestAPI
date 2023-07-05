from django.test import TestCase
from tickets.models import TicketThread


class TicketThreadTest(TestCase):
    def setUp(self):
        self.ticket_thread = TicketThread.objects.create()

    def test_ticket_thread_creation(self):
        self.assertIsInstance(self.ticket_thread, TicketThread)

    def test_default_status(self):
        self.assertEqual(self.ticket_thread.status, 'A')
