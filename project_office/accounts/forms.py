from django import forms
from django.contrib.auth.models import User

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите логин",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите пароль",
            }
        ),
    )

    remember_me = forms.BooleanField(
        label="Запомнить меня",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    full_name = forms.CharField(
        label="ФИО",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    role = forms.ChoiceField(
        label="Роль",
        choices=Profile.Role.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    is_blocked = forms.BooleanField(
        label="Заблокирован",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
        ]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

        labels = {
            "username": "Логин",
            "email": "Email",
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True

        if commit:
            user.save()

            profile = user.profile
            profile.full_name = self.cleaned_data["full_name"]
            profile.role = self.cleaned_data["role"]
            profile.is_blocked = self.cleaned_data["is_blocked"]
            profile.save()

        return user


class UserUpdateForm(forms.ModelForm):
    full_name = forms.CharField(
        label="ФИО",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    role = forms.ChoiceField(
        label="Роль",
        choices=Profile.Role.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    is_blocked = forms.BooleanField(
        label="Заблокирован",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "is_active",
        ]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

        labels = {
            "username": "Логин",
            "email": "Email",
            "is_active": "Активен",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and hasattr(self.instance, "profile"):
            self.fields["full_name"].initial = self.instance.profile.full_name
            self.fields["role"].initial = self.instance.profile.role
            self.fields["is_blocked"].initial = self.instance.profile.is_blocked

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()

            profile = user.profile
            profile.full_name = self.cleaned_data["full_name"]
            profile.role = self.cleaned_data["role"]
            profile.is_blocked = self.cleaned_data["is_blocked"]
            profile.save()

        return user