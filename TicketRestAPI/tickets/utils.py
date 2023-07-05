import imapclient
import email
import re
from django.conf import settings
from .models import Ticket, TicketThread


def get_emails():
    # Conecta-se ao servidor de e-mail configurado e obtém os e-mails da caixa de entrada.
    # Retorna uma lista de dicionários contendo os assuntos e corpos dos e-mails.
    client = imapclient.IMAPClient(settings.MAIL_SERVER)

    client.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)

    client.select_folder('INBOX')

    messages = client.search([u'FROM', settings.MAIL_USERNAME])

    response = client.fetch(messages, ['BODY[]'])

    emails = []
    for msgid, data in response.items():
        raw_email = data[b'BODY[]']
        email_message = email.message_from_bytes(raw_email)
        subject = email_message.get('Subject', '')
        body = get_body(email_message)
        emails.append({'subject': subject, 'body': body})
    return emails


def get_body(email_message):
    # Extrai o corpo de um e-mail.
    # Se o e-mail for multipart, retorna o corpo do primeiro texto encontrado.
    # Caso contrário, retorna o corpo do próprio e-mail.
    if email_message.is_multipart():
        for part in email_message.get_payload():
            if part.get_content_type() == 'text/plain':
                return part.get_payload()
    else:
        return email_message.get_payload()


def extract_code_from_subject(subject):
    # Extrai o código entre colchetes do assunto do e-mail.
    match = re.search(r'\[(.*?)\]', subject)
    return match.group(1) if match else None


def create_or_update_ticket(subject, body, code):
    # Cria ou atualiza um ticket com base no código.
    # Retorna a instância do ticket criado ou atualizado.
    thread, _ = TicketThread.objects.get_or_create(thread_code=code)
    ticket, created = Ticket.objects.get_or_create(code=code,
                                                   defaults={'title': subject, 'body': body, 'thread': thread})
    if not created:
        ticket.title = subject
        ticket.body = body
        ticket.thread = thread
        ticket.save()
    return ticket


def update_ticket_and_thread_status(ticket_instance, subject):
    # Atualiza o status do ticket e do thread com base no assunto do e-mail.
    # Se o assunto contiver "fechado" ou "resolvido", o status é definido como "closed".
    if "fechado" in subject or "resolvido" in subject:
        ticket_instance.status = "closed"
        ticket_instance.save()
        thread = TicketThread.objects.get(tickets=ticket_instance)
        thread.status = "closed"
        thread.save()


def fetch_and_process_emails():
    # Obtém os e-mails, cria ou atualiza os tickets correspondentes e atualiza os status.
    emails = get_emails()
    for email_data in emails:
        title = email_data['subject']
        body = email_data['body']
        code = extract_code_from_subject(title)
        if code is None:
            print(f"Could not extract code from email with title: {title}")
            continue
        ticket_instance = create_or_update_ticket(title, body, code)
        update_ticket_and_thread_status(ticket_instance, title)
