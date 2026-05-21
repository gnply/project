from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "project",
        "user",
        "action",
        "model_name",
        "object_id",
    )

    list_filter = (
        "created_at",
        "user",
        "model_name",
    )

    search_fields = (
        "project__title",
        "user__username",
        "user__profile__full_name",
        "action",
        "description",
        "model_name",
    )

    readonly_fields = (
        "created_at",
    )