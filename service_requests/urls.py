from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [

    path(
        "",
        views.service_request_list,
        name="service_request_list"
    ),

    path(
        "create/",
        views.create_service_request,
        name="create_service_request"
    ),

    path(
        "<int:pk>/",
        views.service_request_detail,
        name="service_request_detail"
    ),

    path(
        "<int:pk>/update/",
        views.update_service_request,
        name="update_service_request"
    ),

    path(
        "<int:pk>/comment/",
        views.add_service_request_comment,
        name="add_service_request_comment"
    ),

    path(
        "<int:pk>/attachment/",
        views.add_service_request_attachment,
        name="add_service_request_attachment"
    ),
]