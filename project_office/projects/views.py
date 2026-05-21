from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from software.models import Software
from .models import City, Project, ProjectStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from audit.models import AuditLog
from contacts.forms import ProjectContactForm
from documents.forms import ProjectDocumentForm
from equipment.forms import ProjectEquipmentForm, ProductionEquipmentForm
from equipment.models import ProductionEquipment
from software.forms import SoftwareUpdateForm

from .forms import ProjectForm

from accounts.permissions import (
    can_access_production,
    can_create_project,
    can_edit_project,
    can_manage_project_contacts,
    can_manage_project_documents,
    can_manage_project_equipment,
    can_manage_project_software,
)

from contacts.models import ProjectContact
from documents.models import ProjectDocument
from equipment.models import ProjectEquipment
from software.models import SoftwareUpdate

import os

from django.http import FileResponse, Http404

@login_required
def project_list(request):
    projects = (
        Project.objects
        .select_related(
            "city",
            "status",
            "manager",
            "manager__profile",
            "software",
            "final_customer",
        )
        .all()
    )

    q = request.GET.get("q")
    status = request.GET.get("status")
    city = request.GET.get("city")
    software = request.GET.get("software")
    version = request.GET.get("version")

    if q:
        projects = projects.filter(
            Q(title__icontains=q)
            | Q(city__name__icontains=q)
            | Q(final_customer__name__icontains=q)
            | Q(contract_customer__name__icontains=q)
            | Q(manager__username__icontains=q)
            | Q(manager__profile__full_name__icontains=q)
            | Q(active_software_version__icontains=q)
        )

    if status:
        projects = projects.filter(status_id=status)

    if city:
        projects = projects.filter(city_id=city)

    if software:
        projects = projects.filter(software_id=software)

    if version:
        projects = projects.filter(active_software_version__icontains=version)

    context = {
        "projects": projects,
        "statuses": ProjectStatus.objects.all(),
        "cities": City.objects.all(),
        "software_list": Software.objects.all(),
        "can_create_project": can_create_project(request.user),
    }

    return render(request, "projects/project_list.html", context)

@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related(
            "city",
            "status",
            "manager",
            "manager__profile",
            "implementer",
            "implementer__profile",
            "software",
            "final_customer",
            "contract_customer",
        ).prefetch_related(
            "tags",
            "contacts",
            "equipment_items",
            "software_updates",
            "documents",
            "history",
        ),
        pk=pk,
    )

    context = {
        "project": project,
        "contacts": project.contacts.select_related("company").all(),
        "equipment_items": project.equipment_items.all(),
        "software_updates": project.software_updates.select_related(
            "responsible",
            "responsible__profile",
        ).all(),
        "documents": project.documents.select_related(
            "category",
            "uploaded_by",
            "uploaded_by__profile",
        ).all(),
        "history": project.history.select_related("user", "user__profile").all(),

        "can_edit_project": can_edit_project(request.user, project),
        "can_manage_contacts": can_manage_project_contacts(request.user, project),
        "can_manage_equipment": can_manage_project_equipment(request.user, project),
        "can_manage_software": can_manage_project_software(request.user, project),
        "can_manage_documents": can_manage_project_documents(request.user, project),
    }

    return render(request, "projects/project_detail.html", context)

    return render(request, "projects/project_detail.html", {"project": project})

@login_required
def add_project_contact(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_contacts(request.user, project):
        messages.error(request, "У вас нет прав на добавление контактов.")
        return redirect("project_detail", pk=project.id)

    if request.method == "POST":
        form = ProjectContactForm(request.POST)

        if form.is_valid():
            contact = form.save(commit=False)
            contact.project = project
            contact.save()

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Добавлен контакт",
                description=f"Добавлен контакт: {contact.full_name}",
                model_name="ProjectContact",
                object_id=contact.id,
            )

            messages.success(request, "Контакт успешно добавлен.")
            return redirect("project_detail", pk=project.id)
    else:
        form = ProjectContactForm()

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": project,
            "title": "Добавить контакт проекта",
        },
    )


@login_required
def add_project_equipment(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_equipment(request.user, project):
        messages.error(request, "У вас нет прав на добавление оборудования.")
        return redirect("project_detail", pk=project.id)

    if request.method == "POST":
        form = ProjectEquipmentForm(request.POST)

        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.project = project
            equipment.save()

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Добавлено оборудование",
                description=f"Добавлено оборудование: {equipment.name}",
                model_name="ProjectEquipment",
                object_id=equipment.id,
            )

            messages.success(request, "Оборудование успешно добавлено.")
            return redirect("project_detail", pk=project.id)
    else:
        form = ProjectEquipmentForm()

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": project,
            "title": "Добавить оборудование проекта",
        },
    )


@login_required
def add_software_update(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_software(request.user, project):
        messages.error(request, "У вас нет прав на добавление обновлений ПО.")
        return redirect("project_detail", pk=project.id)

    if request.method == "POST":
        form = SoftwareUpdateForm(request.POST)

        if form.is_valid():
            update = form.save(commit=False)
            update.project = project
            update.save()

            project.active_software_version = update.version
            project.save(update_fields=["active_software_version", "updated_at"])

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Обновлена версия ПО",
                description=f"Добавлена версия ПО: {update.version}",
                model_name="SoftwareUpdate",
                object_id=update.id,
            )

            messages.success(request, "Запись об обновлении ПО успешно добавлена.")
            return redirect("project_detail", pk=project.id)
    else:
        form = SoftwareUpdateForm()

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": project,
            "title": "Добавить обновление ПО",
        },
    )


@login_required
def upload_project_document(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_documents(request.user, project):
        messages.error(request, "У вас нет прав на загрузку документов.")
        return redirect("project_detail", pk=project.id)

    if request.method == "POST":
        form = ProjectDocumentForm(request.POST, request.FILES)

        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploaded_by = request.user

            uploaded_file = request.FILES.get("file")
            if uploaded_file:
                document.original_name = uploaded_file.name

            document.save()

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Загружен документ",
                description=f"Загружен документ: {document.original_name}",
                model_name="ProjectDocument",
                object_id=document.id,
            )

            messages.success(request, "Документ успешно загружен.")
            return redirect("project_detail", pk=project.id)
    else:
        form = ProjectDocumentForm()

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": project,
            "title": "Загрузить документ проекта",
        },
    )

@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not can_edit_project(request.user, project):
        messages.error(request, "У вас нет прав на редактирование этого проекта.")
        return redirect("project_detail", pk=project.id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Изменена информация о проекте",
                description="Обновлены основные сведения проекта",
                model_name="Project",
                object_id=project.id,
            )

            messages.success(request, "Информация о проекте успешно обновлена.")
            return redirect("project_detail", pk=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": project,
            "title": "Редактировать проект",
        },
    )

@login_required
def production_dashboard(request):
    if not can_access_production(request.user):
        messages.error(request, "У вас нет прав на доступ к модулю «Производство».")
        return redirect("project_list")

    equipment_items = ProductionEquipment.objects.select_related("project").all()

    production_type = request.GET.get("production_type")
    status = request.GET.get("status")
    q = request.GET.get("q")

    if production_type:
        equipment_items = equipment_items.filter(production_type=production_type)

    if status:
        equipment_items = equipment_items.filter(status=status)

    if q:
        equipment_items = equipment_items.filter(name__icontains=q)

    projects = (
        Project.objects
        .select_related("city", "status")
        .prefetch_related("equipment_items", "production_equipment")
        .all()
    )

    context = {
        "equipment_items": equipment_items,
        "projects": projects,
        "production_type_choices": ProductionEquipment.ProductionType.choices,
        "status_choices": ProductionEquipment.Status.choices,
    }

    return render(request, "projects/production_dashboard.html", context)


@login_required
def add_production_equipment(request):
    if not can_access_production(request.user):
        messages.error(request, "У вас нет прав на добавление оборудования производства.")
        return redirect("project_list")

    if request.method == "POST":
        form = ProductionEquipmentForm(request.POST)

        if form.is_valid():
            equipment = form.save()

            AuditLog.objects.create(
                user=request.user,
                action="Добавлено оборудование производства",
                description=f"Добавлено оборудование: {equipment.name}",
                model_name="ProductionEquipment",
                object_id=equipment.id,
            )

            messages.success(request, "Оборудование производства успешно добавлено.")
            return redirect("production_dashboard")
    else:
        form = ProductionEquipmentForm()

    return render(
        request,
        "production_form.html",
        {
            "form": form,
            "title": "Добавить оборудование производства",
        },
    )


@login_required
def attach_production_equipment(request, equipment_id):
    if not can_access_production(request.user):
        messages.error(request, "У вас нет прав на привязку оборудования.")
        return redirect("project_list")

    equipment = get_object_or_404(ProductionEquipment, pk=equipment_id)

    if request.method == "POST":
        project_id = request.POST.get("project")

        if not project_id:
            messages.error(request, "Необходимо выбрать проект.")
            return redirect("production_dashboard")

        project = get_object_or_404(Project, pk=project_id)

        equipment.project = project
        equipment.status = ProductionEquipment.Status.ATTACHED
        equipment.save(update_fields=["project", "status"])

        AuditLog.objects.create(
            project=project,
            user=request.user,
            action="Привязано оборудование производства",
            description=f"К проекту привязано оборудование: {equipment.name}",
            model_name="ProductionEquipment",
            object_id=equipment.id,
        )

        messages.success(request, "Оборудование успешно привязано к проекту.")
        return redirect("production_dashboard")

    return redirect("production_dashboard")


@login_required
def detach_production_equipment(request, equipment_id):
    if not can_access_production(request.user):
        messages.error(request, "У вас нет прав на отвязку оборудования.")
        return redirect("project_list")

    equipment = get_object_or_404(ProductionEquipment, pk=equipment_id)
    old_project = equipment.project

    equipment.project = None
    equipment.status = ProductionEquipment.Status.FREE
    equipment.save(update_fields=["project", "status"])

    AuditLog.objects.create(
        project=old_project,
        user=request.user,
        action="Отвязано оборудование производства",
        description=f"Оборудование отвязано от проекта: {equipment.name}",
        model_name="ProductionEquipment",
        object_id=equipment.id,
    )

    messages.success(request, "Оборудование успешно отвязано от проекта.")
    return redirect("production_dashboard")

@login_required
def create_project(request):
    if not can_create_project(request.user):
        messages.error(request, "У вас нет прав на создание проектов.")
        return redirect("project_list")

    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save()

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Создан проект",
                description=f"Создан проект: {project.title}",
                model_name="Project",
                object_id=project.id,
            )

            messages.success(request, "Проект успешно создан.")
            return redirect("project_detail", pk=project.id)
    else:
        initial_data = {}

        if not request.user.is_superuser:
            initial_data["manager"] = request.user

        form = ProjectForm(initial=initial_data)

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": None,
            "title": "Создать проект",
        },
    )

@login_required
def edit_project_contact(request, pk, contact_id):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_contacts(request.user, project):
        messages.error(request, "У вас нет прав на редактирование контактов.")
        return redirect("project_detail", pk=project.id)

    contact = get_object_or_404(ProjectContact, pk=contact_id, project=project)

    if request.method == "POST":
        form = ProjectContactForm(request.POST, instance=contact)

        if form.is_valid():
            form.save()

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Изменён контакт",
                description=f"Изменён контакт: {contact.full_name}",
                model_name="ProjectContact",
                object_id=contact.id,
            )

            messages.success(request, "Контакт успешно обновлён.")
            return redirect("project_detail", pk=project.id)
    else:
        form = ProjectContactForm(instance=contact)

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": project,
            "title": "Редактировать контакт проекта",
        },
    )


@login_required
def delete_project_contact(request, pk, contact_id):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_contacts(request.user, project):
        messages.error(request, "У вас нет прав на удаление контактов.")
        return redirect("project_detail", pk=project.id)

    contact = get_object_or_404(ProjectContact, pk=contact_id, project=project)
    object_name = contact.full_name

    if request.method == "POST":
        contact.delete()

        AuditLog.objects.create(
            project=project,
            user=request.user,
            action="Удалён контакт",
            description=f"Удалён контакт: {object_name}",
            model_name="ProjectContact",
        )

        messages.success(request, "Контакт успешно удалён.")
        return redirect("project_detail", pk=project.id)

    return render(
        request,
        "confirm_delete.html",
        {
            "project": project,
            "object_name": object_name,
        },
    )

@login_required
def edit_project_equipment(request, pk, equipment_id):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_equipment(request.user, project):
        messages.error(request, "У вас нет прав на редактирование оборудования.")
        return redirect("project_detail", pk=project.id)

    equipment = get_object_or_404(ProjectEquipment, pk=equipment_id, project=project)

    if request.method == "POST":
        form = ProjectEquipmentForm(request.POST, instance=equipment)

        if form.is_valid():
            form.save()

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Изменено оборудование",
                description=f"Изменено оборудование: {equipment.name}",
                model_name="ProjectEquipment",
                object_id=equipment.id,
            )

            messages.success(request, "Оборудование успешно обновлено.")
            return redirect("project_detail", pk=project.id)
    else:
        form = ProjectEquipmentForm(instance=equipment)

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": project,
            "title": "Редактировать оборудование проекта",
        },
    )


@login_required
def delete_project_equipment(request, pk, equipment_id):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_equipment(request.user, project):
        messages.error(request, "У вас нет прав на удаление оборудования.")
        return redirect("project_detail", pk=project.id)

    equipment = get_object_or_404(ProjectEquipment, pk=equipment_id, project=project)
    object_name = f"{equipment.get_equipment_type_display()} — {equipment.name}"

    if request.method == "POST":
        equipment.delete()

        AuditLog.objects.create(
            project=project,
            user=request.user,
            action="Удалено оборудование",
            description=f"Удалено оборудование: {object_name}",
            model_name="ProjectEquipment",
        )

        messages.success(request, "Оборудование успешно удалено.")
        return redirect("project_detail", pk=project.id)

    return render(
        request,
        "confirm_delete.html",
        {
            "project": project,
            "object_name": object_name,
        },
    )

@login_required
def edit_software_update(request, pk, update_id):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_software(request.user, project):
        messages.error(request, "У вас нет прав на редактирование обновлений ПО.")
        return redirect("project_detail", pk=project.id)

    update = get_object_or_404(SoftwareUpdate, pk=update_id, project=project)

    if request.method == "POST":
        form = SoftwareUpdateForm(request.POST, instance=update)

        if form.is_valid():
            update = form.save()

            project.active_software_version = update.version
            project.save(update_fields=["active_software_version", "updated_at"])

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Изменено обновление ПО",
                description=f"Изменена запись версии ПО: {update.version}",
                model_name="SoftwareUpdate",
                object_id=update.id,
            )

            messages.success(request, "Обновление ПО успешно обновлено.")
            return redirect("project_detail", pk=project.id)
    else:
        form = SoftwareUpdateForm(instance=update)

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": project,
            "title": "Редактировать обновление ПО",
        },
    )


@login_required
def delete_software_update(request, pk, update_id):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_software(request.user, project):
        messages.error(request, "У вас нет прав на удаление обновлений ПО.")
        return redirect("project_detail", pk=project.id)

    update = get_object_or_404(SoftwareUpdate, pk=update_id, project=project)
    object_name = f"Версия {update.version} от {update.update_date:%d.%m.%Y}"

    if request.method == "POST":
        update.delete()

        last_update = project.software_updates.order_by("-update_date", "-created_at").first()
        if last_update:
            project.active_software_version = last_update.version
        else:
            project.active_software_version = ""
        project.save(update_fields=["active_software_version", "updated_at"])

        AuditLog.objects.create(
            project=project,
            user=request.user,
            action="Удалено обновление ПО",
            description=f"Удалена запись обновления ПО: {object_name}",
            model_name="SoftwareUpdate",
        )

        messages.success(request, "Обновление ПО успешно удалено.")
        return redirect("project_detail", pk=project.id)

    return render(
        request,
        "confirm_delete.html",
        {
            "project": project,
            "object_name": object_name,
        },
    )

@login_required
def edit_project_document(request, pk, document_id):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_documents(request.user, project):
        messages.error(request, "У вас нет прав на редактирование документов.")
        return redirect("project_detail", pk=project.id)

    document = get_object_or_404(ProjectDocument, pk=document_id, project=project)

    if request.method == "POST":
        form = ProjectDocumentForm(request.POST, request.FILES, instance=document)

        if form.is_valid():
            document = form.save(commit=False)

            uploaded_file = request.FILES.get("file")
            if uploaded_file:
                document.original_name = uploaded_file.name

            document.save()

            AuditLog.objects.create(
                project=project,
                user=request.user,
                action="Изменён документ",
                description=f"Изменён документ: {document.original_name}",
                model_name="ProjectDocument",
                object_id=document.id,
            )

            messages.success(request, "Документ успешно обновлён.")
            return redirect("project_detail", pk=project.id)
    else:
        form = ProjectDocumentForm(instance=document)

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "project": project,
            "title": "Редактировать документ проекта",
        },
    )


@login_required
def delete_project_document(request, pk, document_id):
    project = get_object_or_404(Project, pk=pk)

    if not can_manage_project_documents(request.user, project):
        messages.error(request, "У вас нет прав на удаление документов.")
        return redirect("project_detail", pk=project.id)

    document = get_object_or_404(ProjectDocument, pk=document_id, project=project)
    object_name = document.original_name or document.file.name

    if request.method == "POST":
        file_path = document.file.path if document.file else None

        document.delete()

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        AuditLog.objects.create(
            project=project,
            user=request.user,
            action="Удалён документ",
            description=f"Удалён документ: {object_name}",
            model_name="ProjectDocument",
        )

        messages.success(request, "Документ успешно удалён.")
        return redirect("project_detail", pk=project.id)

    return render(
        request,
        "confirm_delete.html",
        {
            "project": project,
            "object_name": object_name,
        },
    )

@login_required
def download_project_document(request, pk, document_id):
    project = get_object_or_404(Project, pk=pk)
    document = get_object_or_404(ProjectDocument, pk=document_id, project=project)

    if not document.file:
        raise Http404("Файл не найден.")

    file_path = document.file.path

    if not os.path.exists(file_path):
        raise Http404("Файл отсутствует на диске.")

    filename = document.original_name or os.path.basename(file_path)

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=filename,
    )