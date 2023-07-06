from rest_framework import viewsets, permissions, status
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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator  
from django.contrib.auth import authenticate, login

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
 
def get_users(request):
    users = User.objects.all().values('id', 'username')  # Only get the id and username fields
    return JsonResponse(list(users), safe=False)

class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        print("Received POST request")  # add this line
        return super().post(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        print("Dispatching request")  # add this line
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            print(f"User {username} authenticated successfully")  # add this line
            login(self.request, user)
        else:
            print(f"Failed to authenticate user {username}")  # add this line

        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        response = super().form_valid(form)

        # create token after user is logged in
        token, created = Token.objects.get_or_create(user=self.request.user)

        # create Registro instance
        #Registro.objects.create(usuario=self.request.user, data_login=timezone.now())

        # you can add the token to a cookie, or include it in the response body
        response.set_cookie('auth_token', token.key)

        return response
    
    def form_invalid(self, form):
        print("Form is invalid")  # add this line
        return super().form_invalid(form)
    
class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        # This method is called before the view is dispatched.
        # It should return an HttpResponse.

        # update Registro instance
        registro = Registro.objects.filter(usuario=request.user).order_by('-data_login').first()
        if registro:
            registro.data_logout = timezone.now()
            registro.save()

        response = super().dispatch(request, *args, **kwargs)
        return response