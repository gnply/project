from django.db import models
from django.contrib.auth.models import User


class Software(models.Model):
    name = models.CharField(
        "Название ПО",
        max_length=255,
        unique=True
    )

    description = models.TextField(
        "Описание ПО",
        blank=True
    )

    class Meta:
        verbose_name = "Программное обеспечение"
        verbose_name_plural = "Программное обеспечение"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SoftwareUpdate(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="software_updates",
        verbose_name="Проект"
    )

    update_date = models.DateField(
        "Дата обновления"
    )

    responsible = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="software_updates",
        verbose_name="Ответственный"
    )

    version = models.CharField(
        "Версия",
        max_length=100
    )

    changes_description = models.TextField(
        "Описание изменений"
    )

    update_reason = models.TextField(
        "Причина обновления",
        blank=True
    )

    created_at = models.DateTimeField(
        "Дата создания записи",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Обновление ПО"
        verbose_name_plural = "История обновлений ПО"
        ordering = ["-update_date"]

    def __str__(self):
        return f"{self.project} — {self.version}"