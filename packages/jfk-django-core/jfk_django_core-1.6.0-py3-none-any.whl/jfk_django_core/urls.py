import os

from allauth.account.decorators import secure_admin_login
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers

from . import apis, viewsets

app_name = "jfk-django-core"

router = routers.DefaultRouter()
router.register(f"{app_name}/user", viewsets.UserViewSet, basename="user")

# Admin Login
if os.getenv("DJANGO_ADMIN_ALLAUTH_LOGIN", "True") == "True":
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    # Knox
    path("api/auth/login/", apis.TokenLoginView.as_view(), name="login"),
    path("api/auth/logout/", apis.TokenLogoutView.as_view(), name="logout"),
    path("api/auth/logoutall/", apis.TokenLogoutAllView.as_view(), name="logoutall"),
    # Swagger UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(), name="redoc"),
    # Core
    path(f"api/{app_name}/healthcheck/", apis.HealthCheck.as_view(), name="healthcheck"),
    path(f"api/{app_name}/celery-healthcheck/", apis.CeleryHealthCheck.as_view(), name="celery-healthcheck"),
    path(f"api/{app_name}/version-info/", apis.VersionAPIView.as_view(), name="version-info"),
    # Allauth
    path("accounts/", include("allauth.urls")),
]
