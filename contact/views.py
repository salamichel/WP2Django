import logging

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

from contact.forms import ContactForm

logger = logging.getLogger(__name__)


def _send_brevo_emails(contact_msg):
    """Send team notification and automated applicant questionnaire via Brevo API."""
    if not settings.BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not configured, skipping email send")
        return

    try:
        import sib_api_v3_sdk

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.BREVO_API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        from blog.models import SiteSettings
        site_settings = SiteSettings.get_solo()
        sender_email = site_settings.brevo_sender_email or settings.BREVO_SENDER_EMAIL or "contact@revesdechiens.fr"
        sender = {"name": site_settings.association_name or settings.SITE_NAME, "email": sender_email}
        recipient_email = site_settings.contact_email or settings.CONTACT_RECIPIENT_EMAIL or "contact@revesdechiens.fr"

        # 1. Notification to the shelter team
        team_content = (
            f"<h3>Nouveau message reçu via le site Rêves de Chiens</h3>"
            f"<p><strong>Motif:</strong> {contact_msg.get_category_display()}</p>"
            f"<p><strong>Nom:</strong> {contact_msg.name}</p>"
            f"<p><strong>Email:</strong> {contact_msg.email}</p>"
            f"<p><strong>Téléphone:</strong> {contact_msg.phone or 'Non renseigné'}</p>"
            f"<p><strong>Animal concerné:</strong> {contact_msg.animal_name or 'N/A'}</p>"
            f"<p><strong>Sujet:</strong> {contact_msg.subject or '-'}</p>"
            f"<p><strong>Message:</strong></p>"
            f"<div style='background:#f8f9fa;padding:12px;border-left:4px solid #e8734a;margin-top:8px;'>{contact_msg.message}</div>"
        )

        send_team_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": recipient_email}],
            sender=sender,
            subject=f"[{contact_msg.get_category_display()}] Nouveau message de {contact_msg.name}",
            html_content=team_content,
        )
        api_instance.send_transac_email(send_team_email)

        # 2. Automated response with specific questionnaire to applicant
        applicant_subject = f"Rêves de Chiens - Réception de votre demande ({contact_msg.get_category_display()})"
        raw_template = ""

        if contact_msg.category == "adoption":
            raw_template = site_settings.email_template_adoption
        elif contact_msg.category == "abandon":
            raw_template = site_settings.email_template_abandon
        elif contact_msg.category == "fa":
            raw_template = site_settings.email_template_fa

        questionnaire_body = ""
        if raw_template and raw_template.strip():
            from django.template import Template, Context
            tpl = Template(raw_template)
            ctx = Context({
                "name": contact_msg.name,
                "email": contact_msg.email,
                "phone": contact_msg.phone or "",
                "animal_name": contact_msg.animal_name or "un de nos protégés",
                "subject": contact_msg.subject or "",
                "message": contact_msg.message or "",
                "site_settings": site_settings,
            })
            questionnaire_body = tpl.render(ctx)

        if questionnaire_body:
            send_user_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": contact_msg.email}],
                sender=sender,
                subject=applicant_subject,
                html_content=questionnaire_body,
            )
            api_instance.send_transac_email(send_user_email)

    except Exception:
        logger.exception("Failed to send contact emails via Brevo")


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            _send_brevo_emails(contact_msg)
            messages.success(request, "Votre message a bien été envoyé ! Vous allez recevoir un email de confirmation contenant les démarches à suivre.")
            return redirect("contact:contact")
    else:
        # Pre-populate from GET parameters (e.g. ?category=adoption&animal=Max)
        initial_data = {}
        category = request.GET.get("category")
        animal = request.GET.get("animal")
        if category in ["adoption", "abandon", "fa", "autre"]:
            initial_data["category"] = category
        if animal:
            initial_data["animal_name"] = animal
            initial_data["subject"] = f"Demande concernant {animal}"
        form = ContactForm(initial=initial_data)

    return render(request, "contact/contact.html", {"form": form})
