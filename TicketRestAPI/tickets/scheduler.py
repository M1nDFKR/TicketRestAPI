from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.utils import timezone
from tickets.models import Registro
from tickets.utils import fetch_and_process_emails


def check_for_inactivity():
    # Update registro for users who haven't sent a request within the last 15 minutes.
    idle_time = timezone.now() - timezone.timedelta(minutes=15)
    Registro.objects.filter(data_logout=None, data_login__lt=idle_time).update(data_logout=idle_time)


scheduler = BackgroundScheduler()
scheduler.add_job(check_for_inactivity, 'interval', minutes=15)
scheduler.add_job(fetch_and_process_emails, 'interval', minutes=5)
scheduler.start()
