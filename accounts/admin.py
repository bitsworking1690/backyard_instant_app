# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import (
    CustomUser,
    EmailOtp,
    Role,
    Permission,
    Module,
    BlacklistedToken,
)
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib.auth.hashers import make_password
from simple_history.admin import SimpleHistoryAdmin


class UserResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        value = row["password"]
        row["password"] = make_password(value)

    class Meta:
        model = CustomUser


class CustomUserAdmin(UserAdmin, ImportExportModelAdmin, SimpleHistoryAdmin):
    def get_roles(self, obj):
        return ", ".join(role.name for role in obj.role.all())

    get_roles.short_description = "Roles"

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            ("Personal info"),
            {"fields": ("first_name", "last_name", "gender", "role", "token")},
        ),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "role",
                ),
            },
        ),
    )
    list_display = [
        "id",
        "email",
        "first_name",
        "last_name",
        "get_roles",
        "gender",
        "token",
    ]
    search_fields = (
        "email",
        "first_name",
        "last_name",
    )
    readonly_fields = ("token",)
    ordering = ("-id",)
    resource_class = UserResource


admin.site.register(CustomUser, CustomUserAdmin)


class EmailOtpAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ["id", "email", "otp", "is_valid", "stage", "created_at"]
    search_fields = ["otp"]


admin.site.register(EmailOtp, EmailOtpAdmin)


class RoleAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


admin.site.register(Role, RoleAdmin)


class PermissionAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ["id", "name", "module"]
    search_fields = ["name"]


admin.site.register(Permission, PermissionAdmin)


class ModuleAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


admin.site.register(Module, ModuleAdmin)


class BlacklistedTokenAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ["id", "token"]
    readonly_fields = ("token",)


admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)
