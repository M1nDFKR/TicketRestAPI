from datetime import timedelta
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from .models import Ticket, TicketThread, Comment, Registro, Attachment
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import os
import tempfile

class CustomUserAdmin(UserAdmin):
    actions = ['download_user_log_pdf']

    def download_user_log_pdf(self, request, queryset):
        # Obtém o usuário atual
        user = request.user

        # Obtém os nomes dos usuários selecionados
        usernames = [user.username for user in queryset]

        # Cria um arquivo temporário para armazenar o PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file_path = temp_file.name

        # Cria um objeto SimpleDocTemplate para gerar o PDF
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []  # Lista para armazenar os elementos do PDF

        # Obtém os estilos padrão
        styles = getSampleStyleSheet()

        # Define o estilo personalizado para a cor verde
        green_style = ParagraphStyle(
            'green',
            parent=styles['Normal'],
            textColor=colors.green,
            alignment=TA_CENTER
        )

        for user in queryset:
            username = user.username
            login_info = f"Login/Logout Log for User: {username}"

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

                # Verifica se o registro de logout está vazio (ainda não fez logout) e destaca com a cor verde
                if not registro.data_logout:
                    data.append([Paragraph(login_date, green_style), Paragraph("Ativo", green_style), Paragraph("Ativo", green_style)])
                else:
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

        # Lê o conteúdo do arquivo temporário
        with open(file_path, 'rb') as f:
            pdf_content = f.read()

        # Fecha e exclui o arquivo temporário
        temp_file.close()
        os.remove(file_path)

        # Define o nome do arquivo PDF com base nos nomes dos usuários
        filename = "_".join(usernames) + "_log.pdf"

        # Cria uma resposta HTTP com o conteúdo do PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf_content)

        return response

class CustomTicketThreadAdmin(admin.ModelAdmin):
    actions = ['download_ticket_thread_pdf', 'body_ticket']
    list_display = ['thread_code']

    def download_ticket_thread_pdf(self, request, queryset):
        # Cria uma resposta HTTP para o arquivo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_ticket_thread.pdf"'

        # Cria um objeto SimpleDocTemplate para gerar o PDF
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []  # Lista para armazenar os elementos do PDF

        for thread in queryset:
            thread_code = thread.thread_code  # Use o campo thread_code como o nome da thread
            ticket_info = f"Ticket thread: {thread_code}"

            styles = getSampleStyleSheet()
            title = Paragraph(ticket_info, styles['Title'])
            elements.append(title)  # Adiciona o título ao PDF

            # Recupera os tickets da thread e cria a tabela de dados
            tickets = thread.tickets.all()
            data = [['ID', 'Data', 'Hora', 'Status']]
            for ticket in tickets:
                ticket_id = ticket.id
                date = ticket.date + timedelta(days=1)  # Adicione um timedelta para ajustar a data conforme necessário
                created_at = date.strftime('%Y-%m-%d')  # Formate a data como string
                created_time = date.strftime('%H:%M:%S')  # Formate a hora como string
                status = ticket.status

                data.append([str(ticket_id), created_at, created_time, status])  # Converta o ticket_id para uma string

            table = Table(data, colWidths=[1*inch, 1.5*inch, 1*inch, 1*inch])  # Ajuste a largura das colunas conforme necessário
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
    
    def body_ticket(self, request, queryset):
        # Cria uma resposta HTTP para o arquivo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_ticket_body.pdf"'

        # Cria um objeto SimpleDocTemplate para gerar o PDF
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []  # Lista para armazenar os elementos do PDF

        for thread in queryset:
            thread_code = thread.thread_code  # Use o campo thread_code como o nome da thread
            ticket_info = f"Ticket thread: {thread_code}"

            styles = getSampleStyleSheet()
            title = Paragraph(ticket_info, styles['Title'])
            elements.append(title)  # Adiciona o título ao PDF

            # Recupera os tickets da thread e cria a tabela de dados
            tickets = thread.tickets.all()
            data = [['Body']]
            for ticket in tickets:
                data.append([ticket.body.strip()])  # Remove os espaços em branco no início e no final do texto

            table = Table(data, colWidths=[8.5*inch])  # Ajuste a largura das colunas conforme necessário
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6495ED')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
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
admin.site.register(TicketThread, CustomTicketThreadAdmin)
admin.site.register([Ticket, Comment, Registro, Attachment])
