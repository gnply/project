from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
        "role",
        "is_blocked",
        "created_at",
    )
    list_filter = (
        "role",
        "is_blocked",
    )
    search_fields = (
        "user__username",
        "user__email",
        "full_name",
    )
    readonly_fields = (
        "created_at",
    )