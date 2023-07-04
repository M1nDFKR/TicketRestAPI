from rest_framework import serializers
from .models import TicketThread, Ticket, Comment

class TicketThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketThread
        fields = ['id', 'created_at', 'updated_at', 'thread_code', 'status']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'ticket', 'user', 'text', 'created_at', 'updated_at']


class TicketSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'thread', 'title', 'created_at', 'updated_at', 'status', 'code', 'files', 'body', 'comments']
