from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    name = models.CharField(
        "Название города",
        max_length=150,
        unique=True
    )

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Company(models.Model):
    class CompanyType(models.TextChoices):
        FINAL_CUSTOMER = "final_customer", "Конечный заказчик"
        CONTRACT_CUSTOMER = "contract_customer", "Заказчик по договору"
        PARTNER = "partner", "Партнёр"
        OTHER = "other", "Другое"

    name = models.CharField(
        "Название компании",
        max_length=255
    )
    company_type = models.CharField(
        "Тип компании",
        max_length=30,
        choices=CompanyType.choices,
        default=CompanyType.OTHER
    )

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProjectStatus(models.Model):
    name = models.CharField(
        "Название статуса",
        max_length=100,
        unique=True
    )
    color = models.CharField(
        "Цвет",
        max_length=30,
        default="#6c757d",
        help_text="Например: #28a745"
    )

    class Meta:
        verbose_name = "Статус проекта"
        verbose_name_plural = "Статусы проектов"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProjectTag(models.Model):
    name = models.CharField(
        "Название тега",
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = "Тег проекта"
        verbose_name_plural = "Теги проектов"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(
        "Название проекта",
        max_length=255
    )

    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="Город"
    )

    final_customer = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="final_customer_projects",
        verbose_name="Конечный заказчик"
    )

    contract_customer = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="contract_customer_projects",
        verbose_name="Заказчик по договору"
    )

    manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="managed_projects",
        verbose_name="Руководитель проекта"
    )

    implementer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="implemented_projects",
        verbose_name="Ответственный за внедрение",
        null=True,
        blank=True
    )

    status = models.ForeignKey(
        ProjectStatus,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="Статус проекта"
    )

    tags = models.ManyToManyField(
        ProjectTag,
        related_name="projects",
        verbose_name="Теги проекта",
        blank=True
    )

    start_date = models.DateField(
        "Дата начала"
    )

    end_date = models.DateField(
        "Дата окончания",
        null=True,
        blank=True
    )

    delivery_date = models.DateField(
        "Дата поставки",
        null=True,
        blank=True
    )

    software = models.ForeignKey(
        "software.Software",
        on_delete=models.SET_NULL,
        related_name="projects",
        verbose_name="ПО",
        null=True,
        blank=True
    )

    active_software_version = models.CharField(
        "Активная версия ПО",
        max_length=100,
        blank=True
    )

    budget = models.DecimalField(
        "Бюджет проекта",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True
    )

    password_manager_link = models.URLField(
        "Ссылка на менеджер паролей",
        blank=True
    )

    goal = models.TextField(
        "Цель проекта",
        blank=True
    )

    situation_description = models.TextField(
        "Описание ситуации",
        blank=True
    )

    boundaries = models.TextField(
        "Границы проекта",
        blank=True
    )

    limitations = models.TextField(
        "Ограничения",
        blank=True
    )

    key_metrics = models.TextField(
        "Ключевые метрики",
        blank=True
    )

    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        "Дата обновления",
        auto_now=True
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title