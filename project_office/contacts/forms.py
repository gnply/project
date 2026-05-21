from django import forms
from .models import ProjectContact


class ProjectContactForm(forms.ModelForm):
    class Meta:
        model = ProjectContact
        fields = [
            "full_name",
            "position",
            "company",
            "phone",
            "email",
            "notes",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "company": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }