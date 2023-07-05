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
        result = create_or_update_ticket(subject, body, code)

        # Verificações dos métodos chamados nos mocks
        mock_ticket_thread.objects.get_or_create.assert_called_once_with(thread_code=code)
        mock_ticket.objects.get_or_create.assert_called_once_with(
            code=code, defaults={'title': subject, 'body': body, 'thread': mock_thread})

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
    @patch('imapclient.IMAPClient')
    def test_get_emails(self, mock_imapclient):
        # Crie uma instância mock do cliente IMAP
        mock_client = MagicMock()
        mock_imapclient.return_value = mock_client

        # Configure o comportamento de 'login' para que ele não falhe
        mock_client.login.return_value = None

        # Configure o comportamento de 'select_folder'
        mock_client.select_folder.return_value = None

        # Configure o comportamento de 'search'
        mock_client.search.return_value = ['123']

        # Crie um exemplo de resposta para 'fetch'
        fetch_response = {
            '123': {
                b'BODY[]': b"Subject: Test\r\n\r\nThis is a test email."
            }
        }
        mock_client.fetch.return_value = fetch_response

        # Agora, chame a função get_emails
        emails = get_emails()

        # Faça as verificações
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['subject'], 'Test')
        self.assertEqual(emails[0]['body'], 'This is a test email.')

        # Verifique se as funções foram chamadas com os parâmetros corretos
        mock_imapclient.assert_called_once_with(settings.MAIL_SERVER)
        mock_client.login.assert_called_once_with(
            settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        mock_client.select_folder.assert_called_once_with('INBOX')
        mock_client.search.assert_called_once_with(
            [u'FROM', settings.MAIL_USERNAME])
        mock_client.fetch.assert_called_once_with(['123'], ['BODY[]'])


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
