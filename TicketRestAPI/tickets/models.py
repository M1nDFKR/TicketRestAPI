from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.signals import user_logged_out

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
    date = models.DateTimeField(null=True)
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


class Attachment(models.Model):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='uploads')


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

# signal handler function
@receiver(user_logged_in)
def create_registro(sender, request, user, **kwargs):
    print("create_registro is called.")
    Registro.objects.create(usuario=user, data_login=timezone.now())


@receiver(user_logged_out)
def update_registro(sender, request, user, **kwargs):
    print("update_registro is called.")
    registro = Registro.objects.filter(usuario=user).order_by('-data_login').first()
    if registro:
        registro.data_logout = timezone.now()
        registro.save()