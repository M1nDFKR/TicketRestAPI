from django.db import models
from django.contrib.auth.models import User
from django.db import models
import re


class TicketThread(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    thread_code = models.CharField(max_length=14, null=True)
    STATUS_CHOICES = (
        ('A', 'Aberto'),
        ('F', 'Fechado'),
    )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='A')

    def __str__(self):
        return f"Thread ID: {self.id}"


class Ticket(models.Model):
    thread = models.ForeignKey(
        TicketThread, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = (
        ('A', 'Aberto'),
        ('F', 'Fechado'),
    )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='A')
    code = models.CharField(max_length=14)
    files = models.FileField(upload_to='static/uploads', blank=True)
    body = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticket.title} - {self.user.username}"
    
class Registro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registros')
    data_login = models.DateTimeField()
    data_logout = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Registro {self.pk}"
