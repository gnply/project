from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        PROJECT_MANAGER = "project_manager", "Руководитель проекта"
        IMPLEMENTER = "implementer", "Внедренец"
        ENGINEER = "engineer", "Инженер"
        GUEST = "guest", "Гость"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь"
    )
    full_name = models.CharField(
        "ФИО",
        max_length=255,
        blank=True
    )
    role = models.CharField(
        "Роль",
        max_length=30,
        choices=Role.choices,
        default=Role.GUEST
    )
    is_blocked = models.BooleanField(
        "Заблокирован",
        default=False
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return self.full_name or self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()