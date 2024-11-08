# -*- coding: utf-8 -*-
from notifications.models import Notification


def create_notification(email, event_type, message):
    Notification.objects.create(
        email=email, event_type=event_type, message=message, is_sent=True
    )
