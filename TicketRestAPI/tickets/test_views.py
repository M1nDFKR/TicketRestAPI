from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

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
