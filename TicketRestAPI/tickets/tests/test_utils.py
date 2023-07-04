from unittest import mock
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from tickets.utils import get_body
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GetBodyTest(TestCase):

    def test_get_body_for_multipart_message(self):
        # Criar uma mensagem de e-mail multipart
        msg = MIMEMultipart()
        body_part = MIMEText("This is the main content", 'plain')
        msg.attach(body_part)
        attachment_part = MIMEText("This is an attachment", 'plain')
        msg.attach(attachment_part)

        # Testar a função get_body
        body = get_body(msg)
        self.assertEqual(body, "This is the main content")

    def test_get_body_for_singlepart_message(self):
        # Criar uma mensagem de e-mail singlepart
        msg = EmailMessage()
        msg.set_content("This is the content")

        # Testar a função get_body
        body = get_body(msg)
        self.assertEqual(body, "This is the content\n")
