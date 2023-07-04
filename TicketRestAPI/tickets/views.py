from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import TicketThread, Ticket, Comment
from .serializers import TicketThreadSerializer, TicketSerializer, CommentSerializer
from .utils import fetch_and_process_emails
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from unittest import mock

User = get_user_model()


class TicketThreadViewSet(viewsets.ModelViewSet):
    queryset = TicketThread.objects.all().order_by('created_at')
    serializer_class = TicketThreadSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['post'])
    def fetch_emails(self, request):
        fetch_and_process_emails()
        return Response({'status': 'Emails fetched and processed successfully'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Deletion of TicketThread is not allowed.'}, status=status.HTTP_403_FORBIDDEN)

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @mock.patch('myapp.views.TicketViewSet.perform_create')
    def perform_create(self, serializer, mock_create):
        mock_create.return_value = None
        serializer.save()

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @mock.patch('myapp.views.CommentViewSet.perform_create')
    def perform_create(self, serializer, mock_create):
        mock_create.return_value = None
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['delete'])
    def delete_comment(self, request, pk=None):
        comment = self.get_object()
        comment.delete()
        return Response({'status': 'ok'})
