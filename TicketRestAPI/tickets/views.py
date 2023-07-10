from rest_framework import viewsets, permissions, status
from django.contrib.auth import user_logged_in
from django.contrib.auth import user_logged_out
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import TicketThread, Ticket, Comment
from .serializers import TicketThreadSerializer, TicketSerializer, CommentSerializer
from .utils import fetch_and_process_emails
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.views import LoginView , LogoutView
from rest_framework.authtoken.models import Token
from django.http import FileResponse
from django.views.generic import View
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from django.utils import timezone
from .models import Registro
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.authtoken.views import ObtainAuthToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator  
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


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
    

# Classe responsável pela manipulação de comentários
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Salva o objeto Comment criado pelo serializador associado ao usuário atual

    # Ação personalizada para excluir um comentário
    @action(detail=True, methods=['delete'])
    def delete_comment(self, request, pk=None):
        comment = self.get_object()  # Obtém o objeto Comment com base no parâmetro pk
        comment.delete()  # Exclui o comentário
        return Response({'status': 'ok'})  # Retorna uma resposta de sucesso
 
def get_users(request):
    users = User.objects.all().values('id', 'username')  # Only get the id and username fields
    return JsonResponse(list(users), safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_authenticated_user(request):
    user = request.user
    authenticated_user = {
        'username': user.username,
        'id': user.id,
    }
    return JsonResponse(authenticated_user)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        token = Token.objects.get(key=response.data['token'])
        user = token.user

        # Send user_logged_in signal
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        # Log in the user (optional)
        # login(request, user)

        return response
    

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # delete the token to force a login
        request.user.auth_token.delete()

        # send the logout signal
        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)

        return Response({"message": "Logged out successfully"}, status=204)
