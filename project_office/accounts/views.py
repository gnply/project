from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, UserCreateForm, UserUpdateForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from accounts.permissions import can_manage_users
from audit.models import AuditLog

from .models import Profile


def login_view(request):
    if request.user.is_authenticated:
        return redirect("project_list")

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            remember_me = form.cleaned_data["remember_me"]

            user = authenticate(
                request,
                username=username,
                password=password,
            )

            if user is not None:
                if hasattr(user, "profile") and user.profile.is_blocked:
                    messages.error(request, "Пользователь заблокирован.")
                    return render(request, "accounts/login.html", {"form": form})

                login(request, user)

                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 14)
                else:
                    request.session.set_expiry(0)

                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)

                return redirect("project_list")

            messages.error(request, "Неверный логин или пароль.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def user_list(request):
    if not can_manage_users(request.user):
        messages.error(request, "У вас нет прав на управление пользователями.")
        return redirect("project_list")

    users = User.objects.select_related("profile").order_by("username")

    q = request.GET.get("q")
    role = request.GET.get("role")
    status = request.GET.get("status")

    if q:
        users = users.filter(
            username__icontains=q
        ) | users.filter(
            email__icontains=q
        ) | users.filter(
            profile__full_name__icontains=q
        )

    if role:
        users = users.filter(profile__role=role)

    if status == "active":
        users = users.filter(is_active=True, profile__is_blocked=False)

    if status == "blocked":
        users = users.filter(profile__is_blocked=True)

    context = {
        "users": users,
        "roles": Profile.Role.choices,
    }

    return render(request, "accounts/user_list.html", context)


@login_required
def user_create(request):
    if not can_manage_users(request.user):
        messages.error(request, "У вас нет прав на создание пользователей.")
        return redirect("project_list")

    if request.method == "POST":
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user = form.save()

            AuditLog.objects.create(
                user=request.user,
                action="Создан пользователь",
                description=f"Создан пользователь: {user.username}",
                model_name="User",
                object_id=user.id,
            )

            messages.success(request, "Пользователь успешно создан.")
            return redirect("user_list")
    else:
        form = UserCreateForm()

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": "Создать пользователя",
        },
    )


@login_required
def user_update(request, user_id):
    if not can_manage_users(request.user):
        messages.error(request, "У вас нет прав на редактирование пользователей.")
        return redirect("project_list")

    user_obj = get_object_or_404(
        User.objects.select_related("profile"),
        pk=user_id,
    )

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user_obj)

        if form.is_valid():
            user_obj = form.save()

            AuditLog.objects.create(
                user=request.user,
                action="Изменён пользователь",
                description=f"Изменён пользователь: {user_obj.username}",
                model_name="User",
                object_id=user_obj.id,
            )

            messages.success(request, "Пользователь успешно обновлён.")
            return redirect("user_list")
    else:
        form = UserUpdateForm(instance=user_obj)

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": "Редактировать пользователя",
        },
    )


@login_required
def user_toggle_block(request, user_id):
    if not can_manage_users(request.user):
        messages.error(request, "У вас нет прав на блокировку пользователей.")
        return redirect("project_list")

    user_obj = User.objects.select_related("profile").get(pk=user_id)

    if user_obj == request.user:
        messages.error(request, "Нельзя заблокировать самого себя.")
        return redirect("user_list")

    profile = user_obj.profile
    profile.is_blocked = not profile.is_blocked
    profile.save(update_fields=["is_blocked"])

    if profile.is_blocked:
        action = "Пользователь заблокирован"
        messages.success(request, "Пользователь заблокирован.")
    else:
        action = "Пользователь разблокирован"
        messages.success(request, "Пользователь разблокирован.")

    AuditLog.objects.create(
        user=request.user,
        action=action,
        description=f"{action}: {user_obj.username}",
        model_name="User",
        object_id=user_obj.id,
    )

    return redirect("user_list")


@login_required
def user_delete(request, user_id):
    if not can_manage_users(request.user):
        messages.error(request, "У вас нет прав на удаление пользователей.")
        return redirect("project_list")

    user_obj = User.objects.select_related("profile").get(pk=user_id)

    if user_obj == request.user:
        messages.error(request, "Нельзя удалить самого себя.")
        return redirect("user_list")

    object_name = user_obj.username

    if request.method == "POST":
        user_obj.delete()

        AuditLog.objects.create(
            user=request.user,
            action="Удалён пользователь",
            description=f"Удалён пользователь: {object_name}",
            model_name="User",
        )

        messages.success(request, "Пользователь успешно удалён.")
        return redirect("user_list")

    return render(
        request,
        "accounts/user_confirm_delete.html",
        {
            "object_name": object_name,
        },
    )