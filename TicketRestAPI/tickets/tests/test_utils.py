from unittest import mock
from django.test import TestCase
from tickets.utils import fetch_and_process_emails, create_or_update_ticket


class TestUtils(TestCase):
    def setUp(self):
        self.emails = [
            {'subject': '[ABC123] Ticket details',
                'body': 'Hello, this is a test'},
            {'subject': '[XYZ456] Another ticket', 'body': 'Another test'},
        ]
        self.mock_imapclient = mock.MagicMock()
        self.mock_imapclient.IMAPClient.return_value = self.mock_imapclient
        self.mock_imapclient.search.return_value = [1, 2]
        self.mock_imapclient.fetch.return_value = {
            1: {b'BODY[]': self.emails[0]['body'].encode()},
            2: {b'BODY[]': self.emails[1]['body'].encode()},
        }

    def test_fetch_and_process_emails(self):
        mock_imapclient = mock.MagicMock()

        with mock.patch('tickets.utils.imapclient.IMAPClient', return_value=mock_imapclient):
            fetch_and_process_emails()

        assert mock_imapclient.login.called
        assert mock_imapclient.select_folder.called
        assert mock_imapclient.search.called
        assert mock_imapclient.fetch.called

    def test_create_or_update_ticket(self):
        subject = "[ABC123] Ticket details"
        body = "Hello, this is a test"
        code = "ABC123"
        ticket_instance = create_or_update_ticket(subject, body, code)
        self.assertEqual(ticket_instance.title, subject)
        self.assertEqual(ticket_instance.body, body)
        self.assertEqual(ticket_instance.code, code)
