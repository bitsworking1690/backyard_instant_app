# -*- coding: utf-8 -*-
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from utils.enums import Enums
from notifications.common import create_notification
from utils.email import reset_password_email


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    """
    Signal handler for the creation of a reset password token, triggers an email with a reset password link.
    """

    reset_password_url = f"/reset-password/?token={reset_password_token.key}"
    reset_password_email(
        reset_password_token.user.first_name,
        reset_password_token.user.email,
        reset_password_url,
    )
    create_notification(
        email=reset_password_token.user.email,
        event_type=Enums.EMAIL.value,
        message=Enums.RESET_PASSWORD_EMAIL.value,
    )
