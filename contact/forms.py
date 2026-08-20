from django import forms
from contact.models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["category", "animal_name", "name", "email", "phone", "subject", "message"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select", "id": "contact_category_select"}),
            "animal_name": forms.TextInput(attrs={"placeholder": "Ex: Max, Bella... (optionnel)", "class": "form-input"}),
            "name": forms.TextInput(attrs={"placeholder": "Votre nom et prénom", "class": "form-input", "required": True}),
            "email": forms.EmailInput(attrs={"placeholder": "Votre adresse email", "class": "form-input", "required": True}),
            "phone": forms.TextInput(attrs={"placeholder": "Votre numéro de téléphone (optionnel)", "class": "form-input"}),
            "subject": forms.TextInput(attrs={"placeholder": "Sujet de votre message", "class": "form-input"}),
            "message": forms.Textarea(attrs={"placeholder": "Expliquez-nous votre demande en quelques lignes...", "rows": 6, "class": "form-input", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].required = False
        self.fields["animal_name"].required = False
        self.fields["phone"].required = False
        self.fields["subject"].required = False
