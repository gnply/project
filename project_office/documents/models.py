from django.db import models
from django.contrib.auth.models import User


class DocumentCategory(models.Model):
    name = models.CharField(
        "Название категории",
        max_length=255,
        unique=True
    )

    class Meta:
        verbose_name = "Категория документа"
        verbose_name_plural = "Категории документов"
        ordering = ["name"]

    def __str__(self):
        return self.name


def project_document_upload_path(instance, filename):
    return f"projects/{instance.project_id}/documents/{filename}"


class ProjectDocument(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Проект"
    )

    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Категория"
    )

    file = models.FileField(
        "Файл",
        upload_to=project_document_upload_path
    )

    original_name = models.CharField(
        "Исходное имя файла",
        max_length=255,
        blank=True
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="uploaded_documents",
        verbose_name="Автор загрузки"
    )

    comment = models.TextField(
        "Комментарий",
        blank=True
    )

    uploaded_at = models.DateTimeField(
        "Дата загрузки",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Документ проекта"
        verbose_name_plural = "Документы проекта"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.original_name or self.file.name