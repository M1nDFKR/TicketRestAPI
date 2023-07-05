from unittest import mock
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from tickets.utils import create_or_update_ticket
from tickets.models import Ticket, TicketThread

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
