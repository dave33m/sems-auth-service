from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Sems Auth Service (SAS)",
        default_version="v1",
        description="Standalone identity provider for Sems ecosystem",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Swagger
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),

    # Admin
    path("admin/", admin.site.urls),

    # Auth API
    path("auth/", include("authcore.urls")),
]
