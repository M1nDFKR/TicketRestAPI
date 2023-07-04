from unittest import mock
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from tickets.utils import get_emails


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
