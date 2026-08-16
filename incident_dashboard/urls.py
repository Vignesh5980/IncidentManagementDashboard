from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),

    # Web URLs
    path("", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("incidents/", include("incidents.urls")),
    path("problems/", include("problems.urls")),
    path("changes/", include("changes.urls")),
    path("service-requests/", include("service_requests.urls")),

    # API URLs
    path("api/incidents/", include("incidents.api.urls")),

    # API Authentication
    path("api/auth/login/", obtain_auth_token),
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )