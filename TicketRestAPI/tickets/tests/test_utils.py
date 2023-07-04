from unittest import mock
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from tickets.utils import extract_code_from_subject


class ExtractCodeTest(TestCase):

    def test_extract_code_from_subject_with_brackets(self):
        subject = "Support request [12345]"
        code = extract_code_from_subject(subject)
        self.assertEqual(code, "12345")

    def test_extract_code_from_subject_without_brackets(self):
        subject = "Support request 12345"
        code = extract_code_from_subject(subject)
        self.assertIsNone(code)
