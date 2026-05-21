from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Проект",
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
        verbose_name="Пользователь",
        null=True,
        blank=True
    )

    action = models.CharField(
        "Действие",
        max_length=255
    )

    description = models.TextField(
        "Описание",
        blank=True
    )

    model_name = models.CharField(
        "Модель",
        max_length=100,
        blank=True
    )

    object_id = models.PositiveIntegerField(
        "ID объекта",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        "Дата и время",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Запись истории"
        verbose_name_plural = "История изменений"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%d.%m.%Y %H:%M} — {self.action}"