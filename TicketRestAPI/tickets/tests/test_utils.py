from unittest import mock
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from tickets.utils import create_or_update_ticket
from tickets.models import Ticket, TicketThread
from tickets.utils import extract_code_from_subject
from tickets.utils import get_body
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tickets.utils import get_emails
from tickets.utils import fetch_and_process_emails, create_or_update_ticket
from datetime import datetime


# Classe de teste que herda de TestCase para realizar testes unitários
class CreateOrUpdateTicketTest(TestCase):

    # Método de teste para a função create_or_update_ticket
    @patch('tickets.utils.Ticket')  # Decorator para substituir a classe Ticket pelo mock
    @patch('tickets.utils.TicketThread')  # Decorator para substituir a classe TicketThread pelo mock
    def test_create_or_update_ticket(self, mock_ticket_thread, mock_ticket):
        # Mocks das instâncias de TicketThread e Ticket
        mock_thread = mock.MagicMock()
        mock_ticket_instance = mock.MagicMock()

        # Configuração dos retornos dos métodos get_or_create dos mocks
        mock_ticket_thread.objects.get_or_create.return_value = (mock_thread, True)
        mock_ticket.objects.get_or_create.return_value = (mock_ticket_instance, True)

        # Dados de teste
        subject = "Test subject"
        body = "Test body"
        code = "Test code"

        # Chamada da função create_or_update_ticket
        current_datetime = datetime.now()
        result = create_or_update_ticket(subject, body, code, current_datetime)

        # Verificações dos métodos chamados nos mocks
        mock_ticket_thread.objects.get_or_create.assert_called_once_with(thread_code=code)
        mock_ticket.objects.get_or_create.assert_called_once_with(
            code=code, date=current_datetime, defaults={'title': subject, 'body': body, 'thread': mock_thread})

        # Verificação do resultado retornado pela função
        self.assertEqual(result, mock_ticket_instance)

        # Verificações adicionais se get_or_create retornar False
        if not mock_ticket.objects.get_or_create.return_value[1]:
            self.assertEqual(result.title, subject)
            self.assertEqual(result.body, body)
            self.assertEqual(result.thread, mock_thread)


class ExtractCodeTest(TestCase):

    def test_extract_code_from_subject_with_brackets(self):
        subject = "Support request [12345]"
        code = extract_code_from_subject(subject)
        self.assertEqual(code, "12345")

    def test_extract_code_from_subject_without_brackets(self):
        subject = "Support request 12345"
        code = extract_code_from_subject(subject)
        self.assertIsNone(code)


class GetBodyTest(TestCase):

    def test_get_body_for_multipart_message(self):
        # Criar uma mensagem de e-mail multipart
        msg = MIMEMultipart()
        body_part = MIMEText("This is the main content", 'plain')
        msg.attach(body_part)
        attachment_part = MIMEText("This is an attachment", 'plain')
        msg.attach(attachment_part)

        # Testar a função get_body
        body = get_body(msg)
        self.assertEqual(body, "This is the main content")

    def test_get_body_for_singlepart_message(self):
        # Criar uma mensagem de e-mail singlepart
        msg = EmailMessage()
        msg.set_content("This is the content")

        # Testar a função get_body
        body = get_body(msg)
        self.assertEqual(body, "This is the content\n")


class GetEmailsTest(TestCase):
    from unittest import mock
from django.test import TestCase
from django.conf import settings
from tickets.utils import get_emails

class GetEmailsTest(TestCase):

    @mock.patch('tickets.utils.imapclient.IMAPClient')
    @mock.patch('tickets.utils.decode_header')
    @mock.patch('tickets.utils.get_body')
    def test_get_emails(self, mock_get_body, mock_decode_header, mock_imapclient):
        # Setting up the mock objects
        mock_client = mock_imapclient.return_value
        mock_client.login.return_value = None
        mock_client.select_folder.return_value = None
        mock_client.search.return_value = ['msgid1', 'msgid2']
        mock_client.fetch.return_value = {
            'msgid1': {b'BODY[]': 'raw_email_1'},
            'msgid2': {b'BODY[]': 'raw_email_2'},
        }
        mock_email_message = mock.MagicMock()
        mock_email_message.get.return_value = 'Raw Subject'
        mock_decode_header.return_value = [('Decoded Subject', 'utf-8')]
        mock_get_body.return_value = 'Email Body'

        with mock.patch('tickets.utils.email.message_from_bytes', return_value=mock_email_message):
            emails = get_emails()

        # Check the interactions with the mock objects
        mock_imapclient.assert_called_once_with(settings.MAIL_SERVER)
        mock_client.login.assert_called_once_with(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        mock_client.select_folder.assert_called_once_with('INBOX')
        mock_client.search.assert_called_once_with(['FROM', "noreply.escoladigital@min-educ.pt"])
        mock_client.fetch.assert_called_once_with(['msgid1', 'msgid2'], ['BODY[]'])
        mock_decode_header.assert_has_calls([mock.call('Raw Subject'), mock.call('Raw Subject')])
        mock_get_body.assert_has_calls([mock.call(mock_email_message), mock.call(mock_email_message)])

        # Check the returned value
        expected_emails = [
            {'subject': 'Decoded Subject', 'body': 'Email Body'},
            {'subject': 'Decoded Subject', 'body': 'Email Body'},
        ]
        self.assertEqual(emails, expected_emails)


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
        current_datetime = datetime.now()  # provide current date and time
        ticket_instance = create_or_update_ticket(
            subject, body, code, current_datetime)
