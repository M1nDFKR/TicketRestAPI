from unittest import mock
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from tickets.utils import create_or_update_ticket
from tickets.models import Ticket, TicketThread


class CreateOrUpdateTicketTest(TestCase):
    @patch('tickets.utils.Ticket')
    @patch('tickets.utils.TicketThread')
    def test_create_or_update_ticket(self, mock_ticket_thread, mock_ticket):
        # Crie instâncias mock para Ticket e TicketThread
        mock_thread = mock.MagicMock()
        mock_ticket_instance = mock.MagicMock()

        mock_ticket_thread.objects.get_or_create.return_value = (
            mock_thread, True)
        mock_ticket.objects.get_or_create.return_value = (
            mock_ticket_instance, True)

        # Defina os valores que você passará para a função
        subject = "Test subject"
        body = "Test body"
        code = "Test code"

        # Chame a função
        result = create_or_update_ticket(subject, body, code)

        # Verifique se o Ticket e o TicketThread foram chamados corretamente
        mock_ticket_thread.objects.get_or_create.assert_called_once_with(
            thread_code=code)
        mock_ticket.objects.get_or_create.assert_called_once_with(code=code,
                                                                  defaults={'title': subject, 'body': body,
                                                                            'thread': mock_thread})

        # Verifique se o ticket é retornado
        self.assertEqual(result, mock_ticket_instance)

        # Caso o ticket já exista, verifique se ele é atualizado corretamente
        # Se o ticket já existia (não foi criado)
        if not mock_ticket.objects.get_or_create.return_value[1]:
            self.assertEqual(result.title, subject)
            self.assertEqual(result.body, body)
            self.assertEqual(result.thread, mock_thread)
