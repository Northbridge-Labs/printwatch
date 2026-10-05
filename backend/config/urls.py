"""Root URL configuration."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # OpenAPI / Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # Apps
    path("api/", include("apps.accounts.api.urls")),
    path("api/", include("apps.printers.api.urls")),
    path("api/", include("apps.jobs.api.urls")),
    path("api/ingest/", include("apps.jobs.api.urls_internal")),
    path("api/", include("apps.quotas.api.urls")),
    path("api/", include("apps.reporting.api.urls")),
    path("api/", include("apps.alerts.api.urls")),

    # Developer-facing versioned API
    path("api/v1/", include("apps.jobs.api.urls_v1")),
]