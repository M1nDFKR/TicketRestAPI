from django.test import TestCase
from django.contrib.auth.models import User
from tickets.models import Comment, Ticket, TicketThread


class CommentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpass123'
        )
        self.ticket_thread = TicketThread.objects.create()
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            code="Test Code",
            thread=self.ticket_thread
        )
        self.comment = Comment.objects.create(
            ticket=self.ticket,
            user=self.user,
            text="Test comment"
        )

    def test_comment_creation(self):
        self.assertIsInstance(self.comment, Comment)

    def test_comment_text(self):
        self.assertEqual(self.comment.text, "Test comment")

    def test_comment_user(self):
        self.assertEqual(self.comment.user, self.user)

    def test_comment_ticket(self):
        self.assertEqual(self.comment.ticket, self.ticket)
