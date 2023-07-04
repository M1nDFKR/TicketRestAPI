from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
import django
django.setup()

from .factories import CommentFactory
from .serializers import CommentSerializer
from .models import Comment

class CommentViewSetTest(APITestCase):
    def setUp(self):
        pass

    def test_list_comments(self):
        CommentFactory.create_batch(3)

        url = reverse('comments')
        response = self.client.get(url)

<<<<<<< HEAD:TicketRestAPI/tickets/tests/test_views.py
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
=======
>>>>>>> origin/main:TicketRestAPI/tickets/test_views.py
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

<<<<<<< HEAD:TicketRestAPI/tickets/tests/test_views.py
    def test_fetch_emails_with_invalid_method(self):
        # Send a GET request to the fetch_emails endpoint
        response = self.client.get(self.url)
        # Check that the response status code is 405 Method Not Allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # Additional assertions if necessary
=======
    def test_create_comment(self):
        url = reverse('comments')

        data = {
            'ticket': id,
            'user': id,
            'text': 'comments'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, CommentSerializer(instance=Comment.objects.last()).data)

    def test_delete_comment(self):
        comment = CommentFactory()

        url = reverse('delete_comment', kwargs={'pk': comment.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'ok'})
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
>>>>>>> origin/main:TicketRestAPI/tickets/test_views.py
