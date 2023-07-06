from django.contrib import admin
from .models import Ticket, TicketThread, Comment, Registro
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime
from django.utils import timezone
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from datetime import timedelta
from reportlab.lib.pagesizes import letter

class CustomUserAdmin(UserAdmin):
    actions = ['download_user_log_pdf']

    def download_user_log_pdf(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_log.pdf"'

        p = canvas.Canvas(response, pagesize=letter)

        for user in queryset:
            username = user.username
            login_info = f"Login/Logout Log for User: {username}"
            p.setFont("Helvetica-Bold", 14)
            p.drawCentredString(300, 750, login_info)

            registros = Registro.objects.filter(usuario=user).order_by('data_login')
            data = [['Login', 'Logout', 'Tempo de Login']]
            for registro in registros:
                login_date = registro.data_login.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')
                logout_date = registro.data_logout.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S') if registro.data_logout else ""

                duration = registro.data_logout - registro.data_login if registro.data_logout else timedelta(seconds=0)
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                login_duration = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

                data.append([login_date, logout_date, login_duration])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.slateblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            table.wrapOn(p, 400, 600)
            table.drawOn(p, 140, 600)

        p.save()
        return response

admin.site.register(Ticket)
admin.site.register(TicketThread)
admin.site.register(Comment)
admin.site.register(Registro)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)