from django.urls import path

from .views import (
    IncidentListCreateAPIView,
    IncidentDetailAPIView,
)


urlpatterns = [

    path(
        "",
        IncidentListCreateAPIView.as_view(),
        name="api_incident_list_create",
    ),

    path(
        "<int:pk>/",
        IncidentDetailAPIView.as_view(),
        name="api_incident_detail",
    ),

]