from django import forms
from .models import SoftwareUpdate


class SoftwareUpdateForm(forms.ModelForm):
    class Meta:
        model = SoftwareUpdate
        fields = [
            "update_date",
            "responsible",
            "version",
            "changes_description",
            "update_reason",
        ]

        widgets = {
            "update_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "responsible": forms.Select(attrs={"class": "form-select"}),
            "version": forms.TextInput(attrs={"class": "form-control"}),
            "changes_description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "update_reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }