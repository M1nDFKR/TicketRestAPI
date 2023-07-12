import os
import imapclient
from datetime import datetime
from email.utils import parsedate_to_datetime
import email
import re
from django.conf import settings
from .models import Ticket, TicketThread, Attachment
from email.header import decode_header
from django.core.files import File
import tempfile
import hashlib


def get_emails():
    # Conecta-se ao servidor de e-mail configurado e obtém os e-mails da caixa de entrada.
    # Retorna uma lista de dicionários contendo os assuntos e corpos dos e-mails.
    client = imapclient.IMAPClient(settings.MAIL_SERVER)

    client.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)

    client.select_folder('INBOX')

    # messages = client.search(['FROM', "noreply.escoladigital@min-educ.pt"])

    messages = client.search(['FROM', "simaosousasms2006@gmail.com"])

    response = client.fetch(messages, ['BODY[]'])

    emails = []
    for msgid, data in response.items():
        raw_email = data[b'BODY[]']
        email_message = email.message_from_bytes(raw_email)
        raw_subject = email_message.get('Subject', '')
        decoded_header = decode_header(raw_subject)
        subject = ''.join([str(text, charset or 'utf-8') if isinstance(text,
                          bytes) else str(text) for text, charset in decoded_header])
        body = get_body(email_message)

        date_str = email_message.get('Date', None)
        date = parsedate_to_datetime(date_str)

        code = extract_code_from_subject(subject)

        attachments = save_attachments(email_message, code)

        emails.append({'subject': subject, 'body': body,
                      'date': date, 'attachments': attachments})
    return emails


def get_body(email_message):
    # Extrai o corpo de um e-mail.
    # Se o e-mail for multipart, retorna o corpo da parte 'text/html', se disponível.
    # Caso contrário, retorna a parte 'text/plain' ou o corpo do próprio e-mail.
    body = None
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == 'text/html' and part.get('Content-Disposition') is None:
                body = part.get_payload(decode=True)
                break 
    else:
        body = email_message.get_payload(decode=True)
    return body.decode('utf-8')



def extract_code_from_subject(subject):
    code_regex = r"\[(.*?)\]"
    match = re.search(code_regex, subject)
    return match.group(1) if match else None


def create_or_update_ticket(subject, body, code, date):
    # Cria ou atualiza um ticket com base no código e na data.
    # Retorna a instância do ticket criado ou atualizado.
    thread, _ = TicketThread.objects.get_or_create(thread_code=code)

    ticket, created = Ticket.objects.get_or_create(
        code=code,
        date=date,
        defaults={
            'title': subject,
            'body': body,
            'thread': thread,
            'date': date
        }
    )
    if not created:
        # update the ticket only if any of the field has changed.
        if ticket.title != subject or ticket.body != body or ticket.thread != thread or ticket.date != date:
            ticket.title = subject
            ticket.body = body
            ticket.thread = thread
            ticket.date = date
            ticket.save()

    return ticket


def update_ticket_and_thread_status(ticket_instance, subject):
    # Atualiza o status do ticket e do thread com base no assunto do e-mail.
    # Se o assunto contiver "fechado" ou "resolvido", o status é definido como "closed".
    if "fechado" in subject or "resolvido" in subject:
        ticket_instance.status = "F"
        ticket_instance.save()
        thread = TicketThread.objects.get(tickets=ticket_instance)
        thread.status = "F"
        thread.save()


def save_attachments(email_message, code):
    attachments = []
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            file_name = part.get_filename()

            if bool(file_name):
                base_name, ext = os.path.splitext(file_name)
                counter = 1
                new_file_name = f"{base_name}_{code}{ext}"
                while os.path.exists(os.path.join(tempfile.gettempdir(), new_file_name)):
                    new_file_name = f"{base_name}_{code}({counter}){ext}"
                    counter += 1

                file_path = os.path.join(tempfile.gettempdir(), new_file_name)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                attachments.append({'filename': file_name, 'path': file_path}) 

    return attachments


def fetch_and_process_emails():
    print("fetching emails...")
    emails = get_emails()
    for email_data in emails:
        print(email_data)
    for email_data in emails:
        title = email_data['subject']
        body = email_data['body']
        code = extract_code_from_subject(title)
        date = email_data['date']
        attachments = email_data.get('attachments', [])

        if code is None:
            print(f"Could not extract code from email with title: {title}")
            continue
        ticket_instance = create_or_update_ticket(title, body, code, date)
        print(ticket_instance)

        for attachment in attachments:
            with open(attachment['path'], 'rb') as f:
                content = f.read()
                # create a hash of the file content
                content_hash = hashlib.md5(content).hexdigest()

                # check if a file with the same hash already exists
                try:
                    existing_attachment = Attachment.objects.get(
                        hash=content_hash)
                except Attachment.DoesNotExist:
                    # if it doesn't exist, save the file and its hash
                    att_instance = Attachment(
                        ticket=ticket_instance, hash=content_hash)
                    att_instance.file.save(
                        os.path.basename(attachment['path']), File(f))
                    att_instance.save()

            os.remove(attachment['path'])

        update_ticket_and_thread_status(ticket_instance, title)
