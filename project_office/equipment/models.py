from django.db import models


class ProjectEquipment(models.Model):
    class EquipmentType(models.TextChoices):
        DETECTOR = "detector", "Детектор"
        SERVER = "server", "Сервер"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="equipment_items",
        verbose_name="Проект"
    )

    equipment_type = models.CharField(
        "Тип оборудования",
        max_length=30,
        choices=EquipmentType.choices
    )

    name = models.CharField(
        "Название",
        max_length=255
    )

    quantity = models.PositiveIntegerField(
        "Количество",
        default=1
    )

    cameras_per_detector = models.PositiveIntegerField(
        "Камер на детектор",
        null=True,
        blank=True
    )

    description = models.TextField(
        "Описание",
        blank=True
    )

    class Meta:
        verbose_name = "Оборудование проекта"
        verbose_name_plural = "Оборудование проекта"
        ordering = ["equipment_type", "name"]

    def __str__(self):
        return f"{self.get_equipment_type_display()} — {self.name}"


class ProductionEquipment(models.Model):
    class ProductionType(models.TextChoices):
        BOARD = "board", "Плата"
        CAMERA = "camera", "Камера"
        SWITCH = "switch", "Коммутатор"
        POWER_SUPPLY = "power_supply", "БП"

    class Status(models.TextChoices):
        FREE = "free", "Свободно"
        ORDERED = "ordered", "Заказ"
        RESERVED = "reserved", "Бронь"
        ATTACHED = "attached", "Привязано"

    production_type = models.CharField(
        "Тип",
        max_length=30,
        choices=ProductionType.choices
    )

    name = models.CharField(
        "Название",
        max_length=255
    )

    quantity = models.PositiveIntegerField(
        "Количество",
        default=1
    )

    status = models.CharField(
        "Статус",
        max_length=30,
        choices=Status.choices,
        default=Status.FREE
    )

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        related_name="production_equipment",
        verbose_name="Проект",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Оборудование производства"
        verbose_name_plural = "Оборудование производства"
        ordering = ["production_type", "name"]

    def __str__(self):
        return f"{self.get_production_type_display()} — {self.name}"