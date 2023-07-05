from django.test import TestCase
from tickets.models import Ticket, TicketThread


class TicketTest(TestCase):
    def setUp(self):
        self.ticket_thread = TicketThread.objects.create()
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            code="Test Code",
            thread=self.ticket_thread
        )

    def test_ticket_creation(self):
        self.assertIsInstance(self.ticket, Ticket)

    def test_default_status(self):
        self.assertEqual(self.ticket.status, 'A')

    def test_ticket_thread(self):
        self.assertEqual(self.ticket.thread, self.ticket_thread)

    def test_ticket_title(self):
        self.assertEqual(self.ticket.title, "Test Ticket")

    def test_ticket_code(self):
        self.assertEqual(self.ticket.code, "Test Code")
