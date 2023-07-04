from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from tickets.factories import TicketThreadFactory, TicketFactory
from unittest.mock import patch
from tickets.models import TicketThread
import django
django.setup()

from tickets.factories import TicketThreadFactory

class TicketThreadViewSetTestCase(APITestCase):
    def setUp(self):
        # Create some TicketThread instances for testing
        self.thread1 = TicketThreadFactory()
        self.thread2 = TicketThreadFactory()
        # Set up the URL for the fetch_emails action
        self.url = reverse('ticketthread-fetch-emails')

        # Create a test user and set up authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.factory = APIRequestFactory()
        self.client.force_authenticate(user=self.user)

    @patch('tickets.views.fetch_and_process_emails')
    def test_fetch_emails(self, mock_fetch_and_process_emails):
        # Configure the mock to return a successful response
        mock_fetch_and_process_emails.return_value = None
        # Send a POST request to the fetch_emails endpoint
        response = self.client.post(self.url)
        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the response data
        self.assertEqual(
            response.data, {'status': 'Emails fetched and processed successfully'}
        )
        # Additional assertions if necessary

    def test_fetch_emails_with_invalid_method(self):
        # Send a GET request to the fetch_emails endpoint
        response = self.client.get(self.url)
        # Check that the response status code is 405 Method Not Allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # Additional assertions if necessary

    def test_retrieving_list_of_ticket_threads(self):
        response = self.client.get(reverse('ticketthread-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieving_single_ticket_thread(self):
        response = self.client.get(reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.thread1.id)

    def test_creating_new_ticket_thread(self):
        data = {'thread_code': '123456789', 'status': 'A'}
        response = self.client.post(reverse('ticketthread-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['thread_code'], '123456789')
        self.assertEqual(response.data['status'], 'A')

    def test_updating_ticket_thread(self):
        staff_user = User.objects.create_user(username='staffuser', password='testpass', is_staff=True)
        self.client.force_authenticate(user=staff_user)

        data = {'thread_code': '987654321', 'status': 'F'}
        response = self.client.put(reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['thread_code'], '987654321')
        self.assertEqual(response.data['status'], 'F')

    def test_deleting_ticket_thread(self):
        staff_user = User.objects.create_user(username='staffuser', password='testpass', is_staff=True)
        self.client.force_authenticate(user=staff_user)

        response = self.client.delete(reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(TicketThread.objects.filter(id=self.thread1.id).exists())

    def test_unauthenticated_requests(self):
        # Unauthenticate the client
        self.client.force_authenticate(user=None)

        # Try to access the list of TicketThreads
        response = self.client.get(reverse('ticketthread-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to access a single TicketThread
        response = self.client.get(reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to create a new TicketThread
        response = self.client.post(reverse('ticketthread-list'), data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to update a TicketThread
        response = self.client.put(reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}), data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to delete a TicketThread
        response = self.client.delete(reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

 

class TicketViewSetTestCase(APITestCase):
    def setUp(self):
        # Create a TicketThread instance for testing
        self.thread = TicketThreadFactory()

        # Create some Ticket instances for testing
        self.ticket1 = TicketFactory(thread=self.thread)
        self.ticket2 = TicketFactory(thread=self.thread)

        # Create a test user and set up authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_retrieving_list_of_tickets(self):
        response = self.client.get(reverse('ticket-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieving_single_ticket(self):
        response = self.client.get(reverse('ticket-detail', kwargs={'pk': self.ticket1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.ticket1.id)

    def test_creating_new_ticket(self):
        data = {
            'thread': self.thread.id,
            'title': 'Test Ticket',
            'code': 'TST0001',
            'status': 'A',
            'body': 'Test Ticket Body',
        }
        response = self.client.post(reverse('ticket-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Ticket')

    def test_updating_ticket(self):
        data = {'title': 'Updated Test Ticket', 'status': 'F'}
        response = self.client.patch(reverse('ticket-detail', kwargs={'pk': self.ticket1.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Test Ticket')
        self.assertEqual(response.data['status'], 'F')

    def test_deleting_ticket(self):
        response = self.client.delete(reverse('ticket-detail', kwargs={'pk': self.ticket1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
