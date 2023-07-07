from datetime import timedelta
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from .models import Ticket, TicketThread, Comment, Registro


class CustomUserAdmin(UserAdmin):
    actions = ['download_user_log_pdf']

    def download_user_log_pdf(self, request, queryset):
        # Cria uma resposta HTTP para o arquivo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_log.pdf"'

        # Cria um objeto SimpleDocTemplate para gerar o PDF
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []  # Lista para armazenar os elementos do PDF

        for user in queryset:
            username = user.username
            login_info = f"Login/Logout Log for User: {username}"

            styles = getSampleStyleSheet()
            title = Paragraph(login_info, styles['Title'])
            elements.append(title)  # Adiciona o título ao PDF

            # Recupera os registros do usuário e cria a tabela de dados
            registros = Registro.objects.filter(
                usuario=user).order_by('data_login')
            data = [['Login', 'Logout', 'Tempo de Login']]
            for registro in registros:
                # Formata as datas e duração para exibição adequada
                login_date = registro.data_login.astimezone(
                    timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')
                logout_date = registro.data_logout.astimezone(
                    timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S') if registro.data_logout else ""

                duration = registro.data_logout - registro.data_login if registro.data_logout else timedelta(
                    seconds=0)
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                login_duration = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

                data.append([login_date, logout_date, login_duration])

            table = Table(data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6495ED')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(table_style)  # Aplica o estilo à tabela

            elements.append(table)  # Adiciona a tabela ao PDF

        doc.build(elements)  # Gera o PDF com os elementos
        return response

class CustomTicketAdmin(admin.ModelAdmin):
    actions = ['download_user_ticket_pdf']

    def download_user_ticket_pdf(self, request, queryset):
        # Cria uma resposta HTTP para o arquivo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_tickets.pdf"'

        # Cria um objeto SimpleDocTemplate para gerar o PDF
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []  # Lista para armazenar os elementos do PDF

        for user in queryset:
            thread_code = user.thread.thread_code  # Use o campo thread_code como o nome da thread
            ticket_info = f"Tickets for User: {thread_code}"

            styles = getSampleStyleSheet()
            title = Paragraph(ticket_info, styles['Title'])
            elements.append(title)  # Adiciona o título ao PDF

            # Recupera os tickets do usuário e cria a tabela de dados
            tickets = Ticket.objects.filter(thread=user.thread)  # Corrigido para thread=user.thread
            data = [['ID', 'Código do Ticket', 'Criado em', 'Status']]
            for ticket in tickets:
                ticket_id = ticket.id
                ticket_code = ticket.code  # Use o campo ticket_code como o código do ticket
                created_at = ticket.created_at.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')
                status = ticket.status

                data.append([str(ticket_id), ticket_code, created_at, status])  # Converta o ticket_id para uma string

            table = Table(data, colWidths=[1*inch, 2*inch, 2*inch, 1*inch])  # Ajuste a largura das colunas conforme necessário
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6495ED')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(table_style)  # Aplica o estilo à tabela

            elements.append(table)  # Adiciona a tabela ao PDF

        doc.build(elements)  # Gera o PDF com os elementos
        return response

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Ticket, CustomTicketAdmin)
admin.site.register([TicketThread, Comment, Registro])
