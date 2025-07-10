# -*- coding: utf-8 -*-
"""
URL configuration for backyard_boiler_plate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import (
    RegularTokenObtainPairView,
    LogoutView,
    GetTokenDetailsView,
    CustomResetPasswordRequestTokenViewSet,
    CustomResetPasswordConfirmViewSet,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="APIs",
        default_version="v1",
        description="APIs Endpoints with Request/Response Formats",
        terms_of_service="",
        contact=openapi.Contact(email="admin@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    path(
        "api/v1/auth/token/",
        RegularTokenObtainPairView.as_view(),
        name="access_token",
    ),
    path(
        "api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="refresh_token"
    ),
    path("api/v1/auth/logout/", LogoutView.as_view(), name="logout"),
    path(
        "api/v1/auth/token/details/",
        GetTokenDetailsView.as_view(),
        name="get_token_details",
    ),
    path(
        "api/v1/auth/password-reset/",
        CustomResetPasswordRequestTokenViewSet.as_view(),
        name="password_reset",
    ),
    path(
        "api/v1/auth/password-reset/confirm/",
        CustomResetPasswordConfirmViewSet.as_view(),
        name="password_reset_confirm",
    ),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/acl/", include("acl.urls")),  # Include ACL app URLs
]
