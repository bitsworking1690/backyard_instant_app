# -*- coding: utf-8 -*-
from django.contrib import admin
from notifications.models import Notification
from import_export.admin import ImportExportModelAdmin


@admin.register(Notification)
class NotificationImportExport(ImportExportModelAdmin):
    list_display = [
        "id",
        "email",
        "event_type",
        "message",
        "is_sent",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "message",
    ]
    search_fields = [
        "email",
    ]
