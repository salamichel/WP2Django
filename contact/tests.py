from django.test import TestCase

from contact.models import ContactMessage


class ContactMessageTest(TestCase):
    def test_create(self):
        msg = ContactMessage.objects.create(
            name="John", email="john@test.com", subject="Hello", message="Test message"
        )
        self.assertIn("John", str(msg))
        self.assertFalse(msg.is_read)
