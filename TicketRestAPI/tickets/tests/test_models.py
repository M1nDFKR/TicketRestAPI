from django.test import TestCase
from django.contrib.auth.models import User
from tickets.models import Comment, Ticket, TicketThread, Attachment
from django.core.files.uploadedfile import SimpleUploadedFile


class TicketThreadTest(TestCase):
    def setUp(self):
        self.ticket_thread = TicketThread.objects.create()

    def test_ticket_thread_creation(self):
        self.assertIsInstance(self.ticket_thread, TicketThread)

    def test_default_status(self):
        self.assertEqual(self.ticket_thread.status, 'A')


class TicketTest(TestCase):
    def setUp(self):
        self.ticket_thread = TicketThread.objects.create()
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            code="Test Code",
            thread=self.ticket_thread,
            date="2023-01-01"  # Adicione uma data de exemplo para o teste
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
            thread=self.ticket_thread,
            date="2023-01-01"  # Adicione uma data de exemplo para o teste
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


class AttachmentTest(TestCase):
    def setUp(self):
        self.ticket_thread = TicketThread.objects.create()
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            code="Test Code",
            thread=self.ticket_thread,
            date="2023-01-01"
        )
        self.file_mock = SimpleUploadedFile('file.txt', b"file_content")
        self.attachment = Attachment.objects.create(
            ticket=self.ticket,
            hash="TestHash",
            file=self.file_mock
        )

    def test_attachment_creation(self):
        self.assertIsInstance(self.attachment, Attachment)

    def test_attachment_hash(self):
        self.assertEqual(self.attachment.hash, "TestHash")

    def test_attachment_ticket(self):
        self.assertEqual(self.attachment.ticket, self.ticket)

    def test_attachment_file(self):
        self.assertEqual(self.attachment.file.read(), b"file_content")
