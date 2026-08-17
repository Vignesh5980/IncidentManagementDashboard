from django.urls import path

from .views import (
    ServiceRequestListCreateAPIView,
    ServiceRequestDetailAPIView,
    ServiceRequestAssignAPIView,
)


urlpatterns = [

    path(
        "",
        ServiceRequestListCreateAPIView.as_view(),
        name="api_service_request_list_create",
    ),

    path(
        "<int:pk>/",
        ServiceRequestDetailAPIView.as_view(),
        name="api_service_request_detail",
    ),

    path(
        "<int:pk>/assign/",
        ServiceRequestAssignAPIView.as_view(),
        name="api_service_request_assign",
    ),

]