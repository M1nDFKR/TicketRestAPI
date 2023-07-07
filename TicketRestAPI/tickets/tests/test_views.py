from tickets.factories import TicketThreadFactory
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from tickets.factories import TicketThreadFactory, TicketFactory
from unittest.mock import patch
from tickets.models import TicketThread
from datetime import datetime

import django
django.setup()


class TicketThreadViewSetTestCase(APITestCase):
    def setUp(self):
        # Configuração inicial para os testes do TicketThreadViewSet

        # Criação de duas instâncias de TicketThread usando TicketThreadFactory
        self.thread1 = TicketThreadFactory()
        self.thread2 = TicketThreadFactory()

        # Definição da URL para o endpoint de busca e criação de um usuário de teste
        self.url = reverse('ticketthread-fetch-emails')
        self.user = User.objects.create_user(
            username='testuser', password='testpass')

        # Criação do cliente de teste e autenticação do usuário
        self.factory = APIRequestFactory()
        self.client.force_authenticate(user=self.user)

    @patch('tickets.views.fetch_and_process_emails')
    def test_fetch_emails(self, mock_fetch_and_process_emails):
        # Teste para buscar e-mails

        # Configuração do mock para a função fetch_and_process_emails
        mock_fetch_and_process_emails.return_value = None

        # Chamada ao endpoint para buscar e-mails
        response = self.client.post(self.url)

        # Verificação dos resultados do teste
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {'status': 'Emails fetched and processed successfully'})

    def test_fetch_emails_with_invalid_method(self):
        # Teste para verificar o comportamento com um método HTTP inválido
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieving_list_of_ticket_threads(self):
        # Teste para obter a lista de threads de tickets
        response = self.client.get(reverse('ticketthread-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieving_single_ticket_thread(self):
        # Teste para obter uma única thread de ticket
        response = self.client.get(
            reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.thread1.id)

    def test_creating_new_ticket_thread(self):
        # Teste para criar uma nova thread de ticket
        data = {'thread_code': '123456789', 'status': 'A'}
        response = self.client.post(reverse('ticketthread-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['thread_code'], '123456789')
        self.assertEqual(response.data['status'], 'A')

    def test_updating_ticket_thread(self):
        # Teste para atualizar uma thread de ticket

        # Criação de um usuário de suporte e autenticação do cliente com esse usuário
        staff_user = User.objects.create_user(
            username='staffuser', password='testpass', is_staff=True)
        self.client.force_authenticate(user=staff_user)

        data = {'thread_code': '987654321', 'status': 'F'}
        response = self.client.put(
            reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['thread_code'], '987654321')
        self.assertEqual(response.data['status'], 'F')

    def test_deleting_ticket_thread(self):
        # Teste para excluir uma thread de ticket

        # Criação de um usuário de suporte e autenticação do cliente com esse usuário
        staff_user = User.objects.create_user(
            username='staffuser', password='testpass', is_staff=True)
        self.client.force_authenticate(user=staff_user)

        response = self.client.delete(
            reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verifica se a thread de ticket ainda existe no banco de dados
        self.assertTrue(TicketThread.objects.filter(
            id=self.thread1.id).exists())

    def test_unauthenticated_requests(self):
        # Teste para requisições não autenticadas

        # Desautentica o cliente
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse('ticketthread-list'))
        self.assertIn(response.status_code, [
                      status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

        response = self.client.get(
            reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}))
        self.assertIn(response.status_code, [
                      status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

        response = self.client.post(reverse('ticketthread-list'), data={})
        self.assertIn(response.status_code, [
                      status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

        response = self.client.put(
            reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}), data={})
        self.assertIn(response.status_code, [
                      status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

        response = self.client.delete(
            reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}))
        self.assertIn(response.status_code, [
                      status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])


class TicketViewSetTestCase(APITestCase):
    def setUp(self):
        # Configuração inicial para os testes do TicketViewSet

        # Criação de uma instância de TicketThread usando TicketThreadFactory
        self.thread = TicketThreadFactory()

        # Criação de duas instâncias de Ticket usando TicketFactory e vinculando à thread criada
        self.ticket1 = TicketFactory(thread=self.thread)
        self.ticket2 = TicketFactory(thread=self.thread)

        # Criação de um usuário de teste e autenticação do cliente com esse usuário
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_retrieving_list_of_tickets(self):
        # Teste para obter a lista de tickets
        response = self.client.get(reverse('ticket-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieving_single_ticket(self):
        # Teste para obter um único ticket
        response = self.client.get(
            reverse('ticket-detail', kwargs={'pk': self.ticket1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.ticket1.id)

    def test_creating_new_ticket(self):
        # Teste para criar um novo ticket
        data = {
            'thread': self.thread.id,
            'title': 'Test Ticket',
            'code': 'TST0001',
            'status': 'A',
            'date': datetime.date.now(),
            'body': 'Test Ticket Body',
        }
        response = self.client.post(reverse('ticket-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Ticket')

    def test_updating_ticket(self):
        # Teste para atualizar um ticket
        data = {'title': 'Updated Test Ticket', 'status': 'F'}
        response = self.client.patch(
            reverse('ticket-detail', kwargs={'pk': self.ticket1.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Test Ticket')
        self.assertEqual(response.data['status'], 'F')

    def test_deleting_ticket(self):
        # Teste para excluir um ticket
        response = self.client.delete(
            reverse('ticket-detail', kwargs={'pk': self.ticket1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
