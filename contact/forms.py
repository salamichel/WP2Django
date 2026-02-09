from django import forms
from contact.models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Votre nom", "class": "form-input"}),
            "email": forms.EmailInput(attrs={"placeholder": "Votre email", "class": "form-input"}),
            "subject": forms.TextInput(attrs={"placeholder": "Sujet", "class": "form-input"}),
            "message": forms.Textarea(attrs={"placeholder": "Votre message", "rows": 6, "class": "form-input"}),
        }
