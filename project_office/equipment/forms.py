from django import forms
from .models import ProjectEquipment, ProductionEquipment


class ProjectEquipmentForm(forms.ModelForm):
    class Meta:
        model = ProjectEquipment
        fields = [
            "equipment_type",
            "name",
            "quantity",
            "cameras_per_detector",
            "description",
        ]

        widgets = {
            "equipment_type": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "cameras_per_detector": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class ProductionEquipmentForm(forms.ModelForm):
    class Meta:
        model = ProductionEquipment
        fields = [
            "production_type",
            "name",
            "quantity",
            "status",
            "project",
        ]

        widgets = {
            "production_type": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "project": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        project = cleaned_data.get("project")

        if status == ProductionEquipment.Status.ATTACHED and not project:
            raise forms.ValidationError(
                "Если оборудование имеет статус «Привязано», необходимо выбрать проект."
            )

        if status != ProductionEquipment.Status.ATTACHED:
            cleaned_data["project"] = None

        return cleaned_data