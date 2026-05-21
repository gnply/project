from django.contrib import admin
from .models import ProjectEquipment, ProductionEquipment


@admin.register(ProjectEquipment)
class ProjectEquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "equipment_type",
        "name",
        "quantity",
        "cameras_per_detector",
    )

    list_filter = (
        "equipment_type",
        "project",
    )

    search_fields = (
        "project__title",
        "name",
        "description",
    )


@admin.register(ProductionEquipment)
class ProductionEquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "production_type",
        "name",
        "quantity",
        "status",
        "project",
        "created_at",
    )

    list_filter = (
        "production_type",
        "status",
        "project",
    )

    search_fields = (
        "name",
        "project__title",
    )

    readonly_fields = (
        "created_at",
    )