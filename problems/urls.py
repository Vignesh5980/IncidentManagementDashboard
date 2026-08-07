from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.problem_list,
        name="problem_list"
    ),

    path(
        "create/",
        views.create_problem,
        name="create_problem"
    ),

    path(
        "<int:pk>/",
        views.problem_detail,
        name="problem_detail"
    ),

    path(
        "<int:pk>/update/",
        views.update_problem,
        name="update_problem"
    ),

    path(
        "<int:pk>/delete/",
        views.delete_problem,
        name="delete_problem"
    ),
    path(

        "<int:pk>/link/",
        views.bulk_link_incidents,
        name="bulk_link_incidents"
    ),
    path(
        "rca/<int:problem_id>/",
        views.rca_detail,
        name="rca_detail"
    ),
    path(
        "rca-dashboard/",
        views.rca_dashboard,
        name="rca_dashboard"
    ),
    path(
        "<int:problem_id>/known-error/create/",
        views.create_known_error,
        name="create_known_error"
    ),
    path(
        "kedb/search/",
        views.search_kedb,
        name="search_kedb"
    ),
]