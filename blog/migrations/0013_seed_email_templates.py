from django.db import migrations


def seed_email_templates(apps, schema_editor):
    SiteSettings = apps.get_model("blog", "SiteSettings")
    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create(id=1)

    adoption_html = (
        "<p>Bonjour {{ name }},</p>\n"
        "<p>Nous vous remercions pour l'intérêt que vous portez à l'association <strong>Rêves de Chiens</strong> concernant votre souhait d'adoption pour <strong>{{ animal_name }}</strong>.</p>\n"
        "<p>Afin d'étudier votre demande et de nous assurer que le profil de l'animal correspond à vos attentes et à votre mode de vie, merci de bien vouloir répondre à ce mail en renseignant ce questionnaire préalable :</p>\n"
        "<div style=\"background:#fdf6f0;padding:16px;border-radius:8px;border:1px solid #fadbd8;margin:16px 0;\">\n"
        "    <h4 style=\"color:#d45a30;margin-top:0;\">📋 Questionnaire Préalable à l'Adoption</h4>\n"
        "    <ol style=\"line-height:1.8;\">\n"
        "        <li><strong>Composition du foyer</strong> : Nombre d'adultes, âges des enfants, autres animaux présents (espèces, âges, stérilisés ?)</li>\n"
        "        <li><strong>Type de logement</strong> : Maison avec jardin clos ? Appartement (quel étage, présence d'un ascenseur / balcon ?)</li>\n"
        "        <li><strong>Votre situation</strong> : Propriétaire ou locataire (accord du propriétaire obtenu ?)</li>\n"
        "        <li><strong>Rythme de vie</strong> : Temps d'absence quotidien de l'animal, présence d'un extérieur accessible en journée ?</li>\n"
        "        <li><strong>Projet & Éducation</strong> : Activités envisagées, balades quotidiennes, méthode d'éducation bienveillante ?</li>\n"
        "        <li><strong>Prévoyance</strong> : Budget vétérinaire / alimentation et solutions de garde pendant vos congés ?</li>\n"
        "        <li><strong>Numéro de téléphone direct</strong> pour vous joindre :</li>\n"
        "    </ol>\n"
        "</div>\n"
        "<p>Dès réception de vos réponses, notre équipe de bénévoles reviendra vers vous très rapidement pour échanger.</p>\n"
        "<p>Bien chaleureusement,<br><strong>L'équipe de l'association Rêves de Chiens</strong><br>100% bénévoles dévoués à la cause animale</p>"
    )

    abandon_html = (
        "<p>Bonjour {{ name }},</p>\n"
        "<p>Nous avons bien reçu votre message concernant une demande de prise en charge pour <strong>{{ animal_name }}</strong>.</p>\n"
        "<p>L'association <strong>Rêves de Chiens</strong> fonctionne uniquement avec des <em>Familles d'Accueil bénévoles</em> (nous n'avons pas de refuge avec box). Nos places sont donc très limitées et réservées aux cas sans autre issue.</p>\n"
        "<div style=\"background:#fdf2e9;padding:16px;border-radius:8px;border:1px solid #f5cba7;margin:16px 0;\">\n"
        "    <h4 style=\"color:#ba4a00;margin-top:0;\">⚠️ Checklist & Renseignements préalables</h4>\n"
        "    <p>Avant toute décision, merci de répondre à ce mail avec les éléments suivants :</p>\n"
        "    <ol style=\"line-height:1.8;\">\n"
        "        <li><strong>Fiche de l'animal</strong> : Nom, espèce, race/croisement, âge précis, numéro d'identification (ICAD), poids approximatif.</li>\n"
        "        <li><strong>Santé</strong> : Carnet de santé à jour ? Vacciné ? Stérilisé/castré ? Problèmes médicaux ou traitements en cours ?</li>\n"
        "        <li><strong>Comportement & Compatibilités</strong> : Entente chiens, entente chats, entente enfants ? Propreté ? Supporte la solitude ? Déjà mordu ou pincé ?</li>\n"
        "        <li><strong>Motif de l'abandon</strong> : Quel est l'événement déclencheur ? Un éducateur canin a-t-il été consulté en cas de trouble du comportement ?</li>\n"
        "        <li><strong>Solutions préalables</strong> : Votre entourage ou vos proches peuvent-ils temporairement vous aider ?</li>\n"
        "        <li><strong>Photos récentes</strong> de l'animal à joindre en réponse à cet email.</li>\n"
        "    </ol>\n"
        "    <p><em>Rappel : Les frais de prise en charge et de mise en règle vétérinaire restent à la charge du cédant. L'association n'assure aucune pension temporaire.</em></p>\n"
        "</div>\n"
        "<p>Nos bénévoles examineront votre demande dès réception de ces détails.</p>\n"
        "<p>Cordialement,<br><strong>L'équipe Rêves de Chiens</strong></p>"
    )

    fa_html = (
        "<p>Bonjour {{ name }},</p>\n"
        "<p>Un immense merci pour votre proposition d'aide en tant que <strong>Famille d'Accueil bénévole</strong> pour Rêves de Chiens ! Sans nos FA, aucun sauvetage ne serait possible.</p>\n"
        "<div style=\"background:#eafaf1;padding:16px;border-radius:8px;border:1px solid #a3e4d7;margin:16px 0;\">\n"
        "    <h4 style=\"color:#1e8449;margin-top:0;\">🏡 Questionnaire Famille d'Accueil</h4>\n"
        "    <p>Pour mieux connaître vos souhaits d'accueil, merci de nous préciser :</p>\n"
        "    <ol style=\"line-height:1.8;\">\n"
        "        <li>Quel type d'animal pouvez-vous accueillir ? (Chiot, chien adulte, chat, chaton, rongeur...)</li>\n"
        "        <li>Votre lieu de résidence (Maison avec jardin clôturé, appartement...) et votre commune/département ?</li>\n"
        "        <li>Avez-vous d'autres animaux chez vous actuellement ?</li>\n"
        "        <li>Votre disponibilité et temps de présence ?</li>\n"
        "    </ol>\n"
        "    <p><em>Rappel : L'association prend en charge l'intégralité des frais vétérinaires de l'animal accueilli et vous accompagne tout au long du séjour !</em></p>\n"
        "</div>\n"
        "<p>Nous vous recontacterons au plus vite pour finaliser votre dossier.</p>\n"
        "<p>Avec toute notre gratitude,<br><strong>L'équipe Rêves de Chiens</strong></p>"
    )

    if not site_settings.email_template_adoption:
        site_settings.email_template_adoption = adoption_html
    if not site_settings.email_template_abandon:
        site_settings.email_template_abandon = abandon_html
    if not site_settings.email_template_fa:
        site_settings.email_template_fa = fa_html

    site_settings.save()


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0012_sitesettings_brevo_sender_email_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_email_templates, migrations.RunPython.noop),
    ]
