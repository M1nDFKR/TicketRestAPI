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


# Classe responsável pela manipulação de threads de tickets
class TicketThreadViewSet(viewsets.ModelViewSet):
    queryset = TicketThread.objects.all().order_by('created_at')  # Consulta para obter todos os objetos TicketThread ordenados pela data de criação
    serializer_class = TicketThreadSerializer  # Classe de serializador usada para converter objetos TicketThread em JSON e vice-versa
    permission_classes = [IsAuthenticatedOrReadOnly]  # Classe de permissões para verificar acesso autenticado ou somente leitura

    # Ação personalizada para buscar e processar e-mails
    @action(detail=False, methods=['post'])
    def fetch_emails(self, request):
        fetch_and_process_emails()  # Função para buscar e processar e-mails
        return Response({'status': 'Emails fetched and processed successfully'}, status=status.HTTP_200_OK)

    # Sobrescreve o método destruir para impedir a exclusão de objetos TicketThread
    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Deletion of TicketThread is not allowed.'}, status=status.HTTP_403_FORBIDDEN)


# Classe responsável pela manipulação de tickets
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()  # Consulta para obter todos os objetos Ticket
    serializer_class = TicketSerializer  # Classe de serializador usada para converter objetos Ticket em JSON e vice-versa
    permission_classes = [IsAuthenticatedOrReadOnly]  # Classe de permissões para verificar acesso autenticado ou somente leitura

    # Sobrescreve o método perform_create para criar um ticket
    @mock.patch('myapp.views.TicketViewSet.perform_create')
    def perform_create(self, serializer, mock_create):
        mock_create.return_value = None  # Define um valor de retorno nulo para a função mock_create
        serializer.save()  # Salva o objeto Ticket criado pelo serializador


# Classe responsável pela manipulação de comentários
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()  # Consulta para obter todos os objetos Comment
    serializer_class = CommentSerializer  # Classe de serializador usada para converter objetos Comment em JSON e vice-versa
    permission_classes = [IsAuthenticatedOrReadOnly]  # Classe de permissões para verificar acesso autenticado ou somente leitura

    # Sobrescreve o método perform_create para criar um comentário
    @mock.patch('myapp.views.CommentViewSet.perform_create')
    def perform_create(self, serializer, mock_create):
        mock_create.return_value = None  # Define um valor de retorno nulo para a função mock_create
        serializer.save(user=self.request.user)  # Salva o objeto Comment criado pelo serializador associado ao usuário atual

    # Ação personalizada para excluir um comentário
    @action(detail=True, methods=['delete'])
    def delete_comment(self, request, pk=None):
        comment = self.get_object()  # Obtém o objeto Comment com base no parâmetro pk
        comment.delete()  # Exclui o comentário
        return Response({'status': 'ok'})  # Retorna uma resposta de sucesso

