from rest_framework import serializers
from .models import TicketThread, Ticket, Comment, User, Attachment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        # Add other fields if necessary

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'ticket', 'user', 'user_id', 'text', 'created_at', 'updated_at']
        # Define o modelo associado ao serializador como Comment
        # Especifica os campos do modelo que serão serializados

class AttachmentSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()

    class Meta:
        model = Attachment  
        fields = ['id', 'file', 'filename']

    def get_filename(self, obj):
        return obj.file.name


class TicketSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)  
    # Define um relacionamento com CommentSerializer para o campo 'comments'
    # many=True indica que pode haver vários objetos relacionados

    class Meta:
        model = Ticket
        fields = ['id', 'thread', 'title', 'date', 'created_at', 'updated_at', 'status', 'code', 'body', 'comments', 'attachments']
        # Define o modelo associado ao serializador como Ticket
        # Especifica os campos do modelo que serão serializados

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['attachments'] = AttachmentSerializer(instance.attachments.all(), many=True).data
        return representation


class TicketThreadSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)  # Add this line
    class Meta:
        model = TicketThread
        fields = ['id', 'created_at', 'updated_at', 'thread_code', 'status', 'tickets']
        # Define o modelo associado ao serializador como TicketThread
        # Especifica os campos do modelo que serão serializados