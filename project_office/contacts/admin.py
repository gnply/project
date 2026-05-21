from django.contrib import admin
from .models import ProjectContact


@admin.register(ProjectContact)
class ProjectContactAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "position",
        "company",
        "phone",
        "email",
        "project",
    )

    list_filter = (
        "company",
        "project",
    )

    search_fields = (
        "full_name",
        "position",
        "company__name",
        "phone",
        "email",
        "project__title",
    )