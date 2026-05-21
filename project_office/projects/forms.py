from django import forms
from django.contrib.auth.models import User

from accounts.models import Profile
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "city",
            "final_customer",
            "contract_customer",
            "manager",
            "implementer",
            "status",
            "tags",
            "start_date",
            "end_date",
            "delivery_date",
            "software",
            "active_software_version",
            "budget",
            "password_manager_link",
            "goal",
            "situation_description",
            "boundaries",
            "limitations",
            "key_metrics",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),

            "city": forms.Select(attrs={"class": "form-select"}),
            "final_customer": forms.Select(attrs={"class": "form-select"}),
            "contract_customer": forms.Select(attrs={"class": "form-select"}),
            "manager": forms.Select(attrs={"class": "form-select"}),
            "implementer": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),

            "tags": forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),

            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "delivery_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),

            "software": forms.Select(attrs={"class": "form-select"}),
            "active_software_version": forms.TextInput(attrs={"class": "form-control"}),

            "budget": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "password_manager_link": forms.URLInput(attrs={"class": "form-control"}),

            "goal": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "situation_description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "boundaries": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "limitations": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "key_metrics": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["manager"].queryset = User.objects.filter(
            profile__role=Profile.Role.PROJECT_MANAGER
        ) | User.objects.filter(
            is_superuser=True
        )

        self.fields["implementer"].queryset = User.objects.filter(
            profile__role=Profile.Role.IMPLEMENTER
        ) | User.objects.filter(
            is_superuser=True
        )

        self.fields["implementer"].required = False
        self.fields["software"].required = False
        self.fields["end_date"].required = False
        self.fields["delivery_date"].required = False
        self.fields["budget"].required = False
        self.fields["password_manager_link"].required = False