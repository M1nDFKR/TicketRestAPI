from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from .factories import TicketThreadFactory, TicketFactory, CommentFactory
from .models import TicketThread, Ticket, Comment
from .serializers import TicketThreadSerializer, TicketSerializer, CommentSerializer
from unittest import mock
from unittest.mock import patch

class CommentViewSetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', email='test@example.com', password='testpassword')
        self.thread = TicketThreadFactory()
        self.ticket = TicketFactory(thread=self.thread)
        self.client = APIClient()

    @patch('.views.CommentViewSet.perform_create')
    def test_create_comment(self, mock_create):
        mock_create.return_value = None
        url = reverse('comment-list')

        data = {
            'ticket': self.ticket.id,
            'user': self.user.id,
            'text': 'comments'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_comments(self):
        CommentFactory(ticket=self.ticket, user=self.user)
        url = reverse('comment-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_comment(self):
        comment = CommentFactory(ticket=self.ticket, user=self.user)
        url = reverse('comment-delete-comment', args=[comment.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())
