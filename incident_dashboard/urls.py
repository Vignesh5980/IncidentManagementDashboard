from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),

    # Web URLs
    path("", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("incidents/", include("incidents.urls")),
    path("problems/", include("problems.urls")),
    path("changes/", include("changes.urls")),
    path("service-requests/", include("service_requests.urls")),

    # JWT Authentication
    path(
        "api/v1/auth/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "api/v1/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    # APIs
    path("api/v1/incidents/", include("incidents.api.urls")),
    path("api/v1/service_request/", include("service_requests.api.urls")),

    # Service Request API
    path(
        "api/service-requests/",
        include("service_requests.api.urls")
    ),


    # OpenAPI Schema
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema"
    ),

    # Swagger UI
    path(
        "api/v1/schema/",
        SpectacularAPIView.as_view(),
        name="schema"
    ),

    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui"
    ),

    path(
        "api/v1/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema"
        ),
        name="redoc"
    ),
]


# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )