from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
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
        data = {'thread_code': '987654321', 'status': 'F'}
        response = self.client.put(reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['thread_code'], '987654321')
        self.assertEqual(response.data['status'], 'F')

    def test_deleting_ticket_thread(self):
        response = self.client.delete(reverse('ticketthread-detail', kwargs={'pk': self.thread1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
