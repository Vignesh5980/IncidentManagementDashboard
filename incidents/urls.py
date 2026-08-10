from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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

    path("kedb/", views.kedb_list, name="kedb_list"),
    path("kedb/create/", views.kedb_create, name="kedb_create"),
]


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
