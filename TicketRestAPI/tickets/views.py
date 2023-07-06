from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import TicketThread, Ticket, Comment
from .serializers import TicketThreadSerializer, TicketSerializer, CommentSerializer
from .utils import fetch_and_process_emails
from django.http import FileResponse
from django.views.generic import View
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from .models import Registro

User = get_user_model()


# Classe responsável pela manipulação de threads de tickets
class TicketThreadViewSet(viewsets.ModelViewSet):
    queryset = TicketThread.objects.all().order_by('created_at')
    serializer_class = TicketThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Ação personalizada para buscar e processar e-mails
    @action(detail=False, methods=['post'])
    def fetch_emails(self, request):
        fetch_and_process_emails()  # Função para buscar e processar e-mails
        return Response({'status': 'Emails fetched and processed successfully'}, status=status.HTTP_200_OK)

    # Sobrescreve o método destruir para impedir a exclusão de objetos TicketThread
    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Deletion of TicketThread is not allowed.'}, status=status.HTTP_403_FORBIDDEN)

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]



# Classe responsável pela manipulação de comentários
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer, mock_create):
        mock_create.return_value = None  # Define um valor de retorno nulo para a função mock_create
        serializer.save(user=self.request.user)  # Salva o objeto Comment criado pelo serializador associado ao usuário atual

    # Ação personalizada para excluir um comentário
    @action(detail=True, methods=['delete'])
    def delete_comment(self, request, pk=None):
        comment = self.get_object()  # Obtém o objeto Comment com base no parâmetro pk
        comment.delete()  # Exclui o comentário
        return Response({'status': 'ok'})  # Retorna uma resposta de sucesso

class PDFView(View):
    def get(self, request, user_id, *args, **kwargs):
        response = FileResponse(self.generate_pdf(user_id), content_type='application/pdf')
        return response

    def generate_pdf(self, user_id):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        # Adicione o texto com informações de login e data ao PDF
        login_info = f"Usuário: {self.request.user.username}"
        login_date = f"Data de Login: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        p.drawString(100, 100, login_info)
        p.drawString(100, 120, login_date)

        # Recupere os registros do usuário específico do banco de dados
        registros = Registro.objects.filter(usuario__id=user_id).order_by('data_login')

        # Adicione os registros ao PDF
        y_position = 140  # Posição vertical inicial para os registros
        for registro in registros:
            registro_info = f"Data de Login: {registro.data_login.strftime('%Y-%m-%d %H:%M:%S')}"
            if registro.data_logout:
                registro_info += f", Data de Logout: {registro.data_logout.strftime('%Y-%m-%d %H:%M:%S')}"
            registro_info += f", Usuário: {registro.usuario.username}"
            p.drawString(100, y_position, registro_info)
            y_position += 20  # Incrementa a posição vertical para o próximo registro

        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer
    



