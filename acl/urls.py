from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, PermissionViewSet, RolePermissionViewSet

router = DefaultRouter()
router.register("roles", RoleViewSet)
router.register("permissions", PermissionViewSet)
router.register("role-permissions", RolePermissionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]