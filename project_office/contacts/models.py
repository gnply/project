from django.db import models


class ProjectContact(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Проект"
    )

    full_name = models.CharField(
        "ФИО",
        max_length=255
    )

    position = models.CharField(
        "Должность",
        max_length=255,
        blank=True
    )

    company = models.ForeignKey(
        "projects.Company",
        on_delete=models.SET_NULL,
        related_name="contacts",
        verbose_name="Компания",
        null=True,
        blank=True
    )

    phone = models.CharField(
        "Телефон",
        max_length=50,
        blank=True
    )

    email = models.EmailField(
        "Email",
        blank=True
    )

    notes = models.TextField(
        "Примечания",
        blank=True
    )

    class Meta:
        verbose_name = "Контакт проекта"
        verbose_name_plural = "Контакты проекта"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name