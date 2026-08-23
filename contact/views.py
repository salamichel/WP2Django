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
        sender = {"name": site_settings.association_name or settings.SITE_NAME, "email": settings.BREVO_SENDER_EMAIL}
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
        questionnaire_body = ""

        if contact_msg.category == "adoption":
            questionnaire_body = f"""
            <p>Bonjour {contact_msg.name},</p>
            <p>Nous vous remercions pour l'intérêt que vous portez à l'association <strong>Rêves de Chiens</strong> concernant votre souhait d'adoption pour <strong>{contact_msg.animal_name or 'un de nos protégés'}</strong>.</p>
            <p>Afin d'étudier votre demande et de nous assurer que le profil de l'animal correspond à vos attentes et à votre mode de vie, merci de bien vouloir répondre à ce mail en renseignant ce questionnaire préalable :</p>
            <div style="background:#fdf6f0;padding:16px;border-radius:8px;border:1px solid #fadbd8;margin:16px 0;">
                <h4 style="color:#d45a30;margin-top:0;">📋 Questionnaire Préalable à l'Adoption</h4>
                <ol style="line-height:1.8;">
                    <li><strong>Composition du foyer</strong> : Nombre d'adultes, âges des enfants, autres animaux présents (espèces, âges, stérilisés ?)</li>
                    <li><strong>Type de logement</strong> : Maison avec jardin clos ? Appartement (quel étage, présence d'un ascenseur / balcon ?)</li>
                    <li><strong>Votre situation</strong> : Propriétaire ou locataire (accord du propriétaire obtenu ?)</li>
                    <li><strong>Rythme de vie</strong> : Temps d'absence quotidien de l'animal, présence d'un extérieur accessible en journée ?</li>
                    <li><strong>Projet & Éducation</strong> : Activités envisagées, balades quotidiennes, méthode d'éducation bienveillante ?</li>
                    <li><strong>Prévoyance</strong> : Budget vétérinaire / alimentation et solutions de garde pendant vos congés ?</li>
                    <li><strong>Numéro de téléphone direct</strong> pour vous joindre :</li>
                </ol>
            </div>
            <p>Dès réception de vos réponses, notre équipe de bénévoles reviendra vers vous très rapidement pour échanger.</p>
            <p>Bien chaleureusement,<br><strong>L'équipe de l'association Rêves de Chiens</strong><br>100% bénévoles dévoués à la cause animale</p>
            """
        elif contact_msg.category == "abandon":
            questionnaire_body = f"""
            <p>Bonjour {contact_msg.name},</p>
            <p>Nous avons bien reçu votre message concernant une demande de prise en charge pour <strong>{contact_msg.animal_name or 'votre animal'}</strong>.</p>
            <p>L'association <strong>Rêves de Chiens</strong> fonctionne uniquement avec des <em>Familles d'Accueil bénévoles</em> (nous n'avons pas de refuge avec box). Nos places sont donc très limitées et réservées aux cas sans autre issue.</p>
            <div style="background:#fdf2e9;padding:16px;border-radius:8px;border:1px solid #f5cba7;margin:16px 0;">
                <h4 style="color:#ba4a00;margin-top:0;">⚠️ Checklist & Renseignements préalables</h4>
                <p>Avant toute décision, merci de répondre à ce mail avec les éléments suivants :</p>
                <ol style="line-height:1.8;">
                    <li><strong>Fiche de l'animal</strong> : Nom, espèce, race/croisement, âge précis, numéro d'identification (ICAD), poids approximatif.</li>
                    <li><strong>Santé</strong> : Carnet de santé à jour ? Vacciné ? Stérilisé/castré ? Problèmes médicaux ou traitements en cours ?</li>
                    <li><strong>Comportement & Compatibilités</strong> : Entente chiens, entente chats, entente enfants ? Propreté ? Supporte la solitude ? Déjà mordu ou pincé ?</li>
                    <li><strong>Motif de l'abandon</strong> : Quel est l'événement déclencheur ? Un éducateur canin a-t-il été consulté en cas de trouble du comportement ?</li>
                    <li><strong>Solutions préalables</strong> : Votre entourage ou vos proches peuvent-ils temporairement vous aider ?</li>
                    <li><strong>Photos récentes</strong> de l'animal à joindre en réponse à cet email.</li>
                </ol>
                <p><em>Rappel : Les frais de prise en charge et de mise en règle vétérinaire restent à la charge du cédant. L'association n'assure aucune pension temporaire.</em></p>
            </div>
            <p>Nos bénévoles examineront votre demande dès réception de ces détails.</p>
            <p>Cordialement,<br><strong>L'équipe Rêves de Chiens</strong></p>
            """
        elif contact_msg.category == "fa":
            questionnaire_body = f"""
            <p>Bonjour {contact_msg.name},</p>
            <p>Un immense merci pour votre proposition d'aide en tant que <strong>Famille d'Accueil bénévole</strong> pour Rêves de Chiens ! Sans nos FA, aucun sauvetage ne serait possible.</p>
            <div style="background:#eafaf1;padding:16px;border-radius:8px;border:1px solid #a3e4d7;margin:16px 0;">
                <h4 style="color:#1e8449;margin-top:0;">🏡 Questionnaire Famille d'Accueil</h4>
                <p>Pour mieux connaître vos souhaits d'accueil, merci de nous préciser :</p>
                <ol style="line-height:1.8;">
                    <li>Quel type d'animal pouvez-vous accueillir ? (Chiot, chien adulte, chat, chaton, rongeur...)</li>
                    <li>Votre lieu de résidence (Maison avec jardin clôturé, appartement...) et votre commune/département ?</li>
                    <li>Avez-vous d'autres animaux chez vous actuellement ?</li>
                    <li>Votre disponibilité et temps de présence ?</li>
                </ol>
                <p><em>Rappel : L'association prend en charge l'intégralité des frais vétérinaires de l'animal accueilli et vous accompagne tout au long du séjour !</em></p>
            </div>
            <p>Nous vous recontacterons au plus vite pour finaliser votre dossier.</p>
            <p>Avec toute notre gratitude,<br><strong>L'équipe Rêves de Chiens</strong></p>
            """

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
