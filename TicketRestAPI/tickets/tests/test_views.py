from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
import django
django.setup()

from .factories import TicketThreadFactory

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
