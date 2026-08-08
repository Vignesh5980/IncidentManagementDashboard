from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("accounts.urls")),

    path("dashboard/", include("dashboard.urls")),

    path("incidents/", include("incidents.urls")),

    path("problems/", include("problems.urls")),

    path("changes/", include("changes.urls")),

    path(
        "service-requests/",
        include("service_requests.urls")
    ),
]


# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )