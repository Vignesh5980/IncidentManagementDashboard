from django.urls import path
from . import views

urlpatterns = [
    path("", views.change_list, name="change_list"),

    path(
        "create/",
        views.change_create,
        name="change_create"
    ),

    path(
        "<int:pk>/",
        views.change_detail,
        name="change_detail"
    ),

    path(
        "<int:pk>/edit/",
        views.change_update,
        name="change_update"
    ),

    path(
        "<int:pk>/delete/",
        views.change_delete,
        name="change_delete"
    ),

    path(
        "<int:pk>/cab/",
        views.cab_approval,
        name="cab_approval"
    ),

    path(
        "calendar/",
        views.change_calendar,
        name="change_calendar"
    ),

    path(
        "<int:pk>/pir/create/",
        views.pir_create,
        name="pir_create"
    ),
]