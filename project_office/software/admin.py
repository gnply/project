from django.contrib import admin
from .models import Software, SoftwareUpdate


@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(SoftwareUpdate)
class SoftwareUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "update_date",
        "responsible",
        "version",
        "created_at",
    )

    list_filter = (
        "update_date",
        "responsible",
        "project",
    )

    search_fields = (
        "project__title",
        "responsible__username",
        "responsible__profile__full_name",
        "version",
        "changes_description",
        "update_reason",
    )

    readonly_fields = (
        "created_at",
    )