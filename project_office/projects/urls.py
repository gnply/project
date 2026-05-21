from django.urls import path
from . import views


urlpatterns = [
    path("", views.project_list, name="project_list"),

    path(
        "projects/create/",
        views.create_project,
        name="create_project",
    ),

    path("projects/<int:pk>/", views.project_detail, name="project_detail"),

    path(
        "projects/<int:pk>/edit/",
        views.edit_project,
        name="edit_project",
    ),

    path(
        "projects/<int:pk>/contacts/add/",
        views.add_project_contact,
        name="add_project_contact",
    ),
    path(
        "projects/<int:pk>/equipment/add/",
        views.add_project_equipment,
        name="add_project_equipment",
    ),
    path(
        "projects/<int:pk>/software-updates/add/",
        views.add_software_update,
        name="add_software_update",
    ),
    path(
        "projects/<int:pk>/documents/upload/",
        views.upload_project_document,
        name="upload_project_document",
    ),
    path(
        "projects/<int:pk>/contacts/<int:contact_id>/edit/",
        views.edit_project_contact,
        name="edit_project_contact",
    ),
    path(
        "projects/<int:pk>/contacts/<int:contact_id>/delete/",
        views.delete_project_contact,
        name="delete_project_contact",
    ),
    path(
        "projects/<int:pk>/documents/<int:document_id>/download/",
        views.download_project_document,
        name="download_project_document",
    ),

    path(
        "projects/<int:pk>/equipment/<int:equipment_id>/edit/",
        views.edit_project_equipment,
        name="edit_project_equipment",
    ),
    path(
        "projects/<int:pk>/equipment/<int:equipment_id>/delete/",
        views.delete_project_equipment,
        name="delete_project_equipment",
    ),

    path(
        "projects/<int:pk>/software-updates/<int:update_id>/edit/",
        views.edit_software_update,
        name="edit_software_update",
    ),
    path(
        "projects/<int:pk>/software-updates/<int:update_id>/delete/",
        views.delete_software_update,
        name="delete_software_update",
    ),

    path(
        "projects/<int:pk>/documents/<int:document_id>/edit/",
        views.edit_project_document,
        name="edit_project_document",
    ),
    path(
        "projects/<int:pk>/documents/<int:document_id>/delete/",
        views.delete_project_document,
        name="delete_project_document",
    ),
    path(
        "production/",
        views.production_dashboard,
        name="production_dashboard",
    ),
    path(
        "production/equipment/add/",
        views.add_production_equipment,
        name="add_production_equipment",
    ),
    path(
        "production/equipment/<int:equipment_id>/attach/",
        views.attach_production_equipment,
        name="attach_production_equipment",
    ),
    path(
        "production/equipment/<int:equipment_id>/detach/",
        views.detach_production_equipment,
        name="detach_production_equipment",
    ),
]