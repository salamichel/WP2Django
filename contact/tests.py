from django.test import TestCase, override_settings
from unittest.mock import patch

from contact.models import ContactMessage
from blog.models import SiteSettings


class ContactMessageTest(TestCase):
    def test_create(self):
        msg = ContactMessage.objects.create(
            name="John", email="john@test.com", subject="Hello", message="Test message"
        )
        self.assertIn("John", str(msg))
        self.assertFalse(msg.is_read)

    @override_settings(BREVO_API_KEY="dummy-key")
    @patch("sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email")
    def test_contact_submission_template_rendering(self, mock_send):
        settings_obj = SiteSettings.get_solo()
        settings_obj.email_template_adoption = "<p>Bonjour {{ name }}, nous traitons votre demande pour {{ animal_name }} !</p>"
        settings_obj.brevo_sender_email = "expediteur@revesdechiens.fr"
        settings_obj.save()

        resp = self.client.post("/contact/", {
            "name": "Alice Dupont",
            "email": "alice@example.com",
            "phone": "0612345678",
            "category": "adoption",
            "animal_name": "Rex",
            "subject": "Adoption Rex",
            "message": "Je souhaite adopter Rex.",
        })

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(mock_send.call_count, 2)
        # Verify applicant email payload
        applicant_email_call = mock_send.call_args_list[1][0][0]
        self.assertEqual(applicant_email_call.to[0]["email"], "alice@example.com")
        self.assertEqual(applicant_email_call.sender["email"], "expediteur@revesdechiens.fr")
        self.assertIn("Bonjour Alice Dupont", applicant_email_call.html_content)
        self.assertIn("Rex", applicant_email_call.html_content)

