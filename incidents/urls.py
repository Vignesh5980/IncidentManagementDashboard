from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.incident_list,
        name='incident_list'
    ),

    path(
        'create/',
        views.create_incident,
        name='create_incident'
    ),

    path(
        '<int:pk>/',
        views.incident_detail,
        name='incident_detail'
    ),

    path(
        '<int:pk>/update/',
        views.update_incident,
        name='update_incident'
    ),
    path(
        "<int:pk>/delete/",
        views.delete_incident,
        name="delete_incident",
    ),
    path(
        "export/csv/",
        views.export_incidents_csv,
        name="export_incidents_csv",
    ),
]