import logging

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

from contact.forms import ContactForm

logger = logging.getLogger(__name__)


def _send_brevo_email(contact_msg):
    """Send notification email via Brevo API."""
    if not settings.BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not configured, skipping email send")
        return

    try:
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.BREVO_API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": settings.BREVO_API_KEY and "admin@example.com"}],
            sender={"name": settings.SITE_NAME, "email": "noreply@example.com"},
            subject=f"[Contact] {contact_msg.subject or 'Nouveau message'}",
            html_content=(
                f"<h3>Nouveau message de contact</h3>"
                f"<p><strong>Nom:</strong> {contact_msg.name}</p>"
                f"<p><strong>Email:</strong> {contact_msg.email}</p>"
                f"<p><strong>Sujet:</strong> {contact_msg.subject}</p>"
                f"<p><strong>Message:</strong></p>"
                f"<p>{contact_msg.message}</p>"
            ),
        )
        api_instance.send_transac_email(send_smtp_email)
    except Exception:
        logger.exception("Failed to send contact email via Brevo")


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            _send_brevo_email(contact_msg)
            messages.success(request, "Votre message a bien été envoyé. Merci !")
            return redirect("contact:contact")
    else:
        form = ContactForm()
    return render(request, "contact/contact.html", {"form": form})
