from django.contrib import admin
from .models import Ticket, TicketThread, Comment

admin.site.register(Ticket)
admin.site.register(TicketThread)
admin.site.register(Comment)
