from django.urls import path
from .views import (
    IncidentListCreateAPIView,
    IncidentDetailAPIView,
)

urlpatterns = [
    path(
        "",
        IncidentListCreateAPIView.as_view(),
        name="incident-list-create"
    ),

    path(
        "<int:pk>/",
        IncidentDetailAPIView.as_view(),
        name="incident-detail"
    ),
]