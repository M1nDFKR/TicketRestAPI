import imapclient
import email
import re
from django.conf import settings
from .models import Ticket, TicketThread

def get_emails():
    # Create an IMAP client
    client = imapclient.IMAPClient(settings.MAIL_SERVER)
    
    # Login to the account
    client.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
    
    # Select the mailbox you want to delete in
    # If you want SPAM, use "INBOX.SPAM"
    client.select_folder('INBOX')
    
    # Search for specific mail by sender
    messages = client.search([u'FROM', settings.MAIL_USERNAME])
    
    # Fetch the mails
    response = client.fetch(messages, ['BODY[]'])
    
    emails = []
    for msgid, data in response.items():
        raw_email = data[b'BODY[]']
        email_message = email.message_from_bytes(raw_email)
        subject = email_message.get('Subject', '')
        body = get_body(email_message)
        emails.append({'subject': subject, 'body': body})
    return emails

def parse_email(msg):
    # Parse a single email
    email_message = email.message_from_string(msg)
    return email_message

def get_body(email_message):
    if email_message.is_multipart():
        for part in email_message.get_payload():
            if part.get_content_type() == 'text/plain':
                return part.get_payload()
    else:
        return email_message.get_payload()

def extract_code_from_subject(subject):
    # Extract code from subject using regex
    match = re.search(r'\[(.*?)\]', subject)
    return match.group(1) if match else None

def create_or_update_ticket(subject, body, code):
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
    # Update status if subject contains "fechado/resolvido"
    if "fechado" in subject or "resolvido" in subject:
        ticket_instance.status = "closed"
        ticket_instance.save()
        thread = TicketThread.objects.get(tickets=ticket_instance)
        thread.status = "closed"
        thread.save()
              
def fetch_and_process_emails():
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