from rest_framework import serializers
from .models import TicketThread, Ticket, Comment

class TicketThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketThread
        fields = ['id', 'created_at', 'updated_at', 'thread_code', 'status']
        # Define o modelo associado ao serializador como TicketThread
        # Especifica os campos do modelo que serão serializados

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'ticket', 'user', 'text', 'created_at', 'updated_at']
        # Define o modelo associado ao serializador como Comment
        # Especifica os campos do modelo que serão serializados

class TicketSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    # Define um relacionamento com CommentSerializer para o campo 'comments'
    # many=True indica que pode haver vários objetos relacionados

    class Meta:
        model = Ticket
        fields = ['id', 'thread', 'title', 'created_at', 'updated_at', 'status', 'code', 'files', 'body', 'comments']
        # Define o modelo associado ao serializador como Ticket
        # Especifica os campos do modelo que serão serializados
