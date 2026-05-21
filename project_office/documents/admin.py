from django.contrib import admin
from .models import DocumentCategory, ProjectDocument


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "category",
        "original_name",
        "uploaded_by",
        "uploaded_at",
    )

    list_filter = (
        "category",
        "project",
        "uploaded_by",
        "uploaded_at",
    )

    search_fields = (
        "project__title",
        "category__name",
        "original_name",
        "comment",
    )

    readonly_fields = (
        "uploaded_at",
    )