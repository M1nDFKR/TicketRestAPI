from django.contrib import admin
from .models import Ticket, TicketThread, Comment, Registro

admin.site.register(Ticket)
admin.site.register(TicketThread)
admin.site.register(Comment)
admin.site.register(Registro)