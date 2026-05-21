from django.urls import path

from . import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("users/", views.user_list, name="user_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<int:user_id>/edit/", views.user_update, name="user_update"),
    path("users/<int:user_id>/toggle-block/", views.user_toggle_block, name="user_toggle_block"),
    path("users/<int:user_id>/delete/", views.user_delete, name="user_delete"),
]