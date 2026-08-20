from django.db import models


class ContactMessage(models.Model):
    CATEGORY_CHOICES = [
        ("adoption", "Demande d'adoption"),
        ("abandon", "Demande de prise en charge / Abandon"),
        ("fa", "Devenir Famille d'Accueil / Bénévolat"),
        ("autre", "Autre question / Renseignement"),
    ]

    name = models.CharField("Nom complet", max_length=255)
    email = models.EmailField("Adresse email")
    phone = models.CharField("Téléphone", max_length=50, blank=True, default="")
    category = models.CharField("Motif de contact", max_length=20, choices=CATEGORY_CHOICES, default="autre", blank=True)
    animal_name = models.CharField("Nom de l'animal concerné", max_length=255, blank=True, default="")
    subject = models.CharField("Sujet", max_length=512, blank=True, default="")
    message = models.TextField("Votre message")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField("Lu", default=False)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name} - {self.subject or self.animal_name or 'Message'}"
