from django.contrib import admin
from .models import City, Company, ProjectStatus, ProjectTag, Project


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company_type",
    )
    list_filter = (
        "company_type",
    )
    search_fields = (
        "name",
    )


@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
    )
    search_fields = (
        "name",
    )


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )
    search_fields = (
        "name",
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "city",
        "status",
        "manager",
        "implementer",
        "software",
        "active_software_version",
        "delivery_date",
        "budget",
        "created_at",
    )

    list_filter = (
        "status",
        "city",
        "manager",
        "implementer",
        "software",
        "tags",
    )

    search_fields = (
        "title",
        "city__name",
        "final_customer__name",
        "contract_customer__name",
        "manager__username",
        "manager__profile__full_name",
        "implementer__username",
        "implementer__profile__full_name",
        "active_software_version",
        "goal",
    )

    filter_horizontal = (
        "tags",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "city",
                    "final_customer",
                    "contract_customer",
                    "manager",
                    "implementer",
                    "status",
                    "tags",
                )
            },
        ),
        (
            "Сроки",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "delivery_date",
                )
            },
        ),
        (
            "Программное обеспечение",
            {
                "fields": (
                    "software",
                    "active_software_version",
                )
            },
        ),
        (
            "Финансы и доступы",
            {
                "fields": (
                    "budget",
                    "password_manager_link",
                )
            },
        ),
        (
            "Описание проекта",
            {
                "fields": (
                    "goal",
                    "situation_description",
                    "boundaries",
                    "limitations",
                    "key_metrics",
                )
            },
        ),
        (
            "Служебная информация",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )