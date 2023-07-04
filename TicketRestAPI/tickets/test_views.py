from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

import django
django.setup()

from .factories import TicketFactory, TicketThreadFactory


class TicketAPITests(APITestCase):
    def setUp(self):
        self.ticket_thread = TicketThreadFactory()
        self.ticket = TicketFactory(thread=self.ticket_thread)
        
    def test_get_ticket_list(self):
        url = reverse('ticket-list')  # replace 'ticket-list' with your actual url name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
