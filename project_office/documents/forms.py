import os

from django import forms

from .models import ProjectDocument


class ProjectDocumentForm(forms.ModelForm):
    MAX_FILE_SIZE = 500 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        ".doc",
        ".docx",
        ".pdf",
        ".ppt",
        ".pptx",
        ".txt",
        ".jpg",
        ".jpeg",
        ".png",
        ".xlsx",
        ".xls",
        ".csv",
        ".zip",
        ".rar",
    }

    class Meta:
        model = ProjectDocument
        fields = [
            "category",
            "file",
            "comment",
        ]

        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")

        if not file:
            return file

        if file.size > self.MAX_FILE_SIZE:
            raise forms.ValidationError(
                "Размер файла не должен превышать 500 МБ."
            )

        extension = os.path.splitext(file.name)[1].lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                "Недопустимый формат файла. Разрешены: doc, docx, pdf, ppt, pptx, txt, jpg, png, xlsx, xls, csv, zip, rar."
            )

        return file