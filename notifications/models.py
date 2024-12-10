# -*- coding: utf-8 -*-
from django.db import models
from utils.models import BaseModel
from utils.enums import Enums


event_type_choices = (
    (Enums.EMAIL.value, "email"),
    (Enums.WHATSAPP.value, "whatsapp"),
    (Enums.SMS.value, "sms"),
    (Enums.API.value, "api"),
)


event_message_choices = (
    (Enums.SIGN_UP_OTP_EMAIL.value, "sign_up_otp_email"),
    (Enums.LOGIN_OTP_EMAIL.value, "login_otp_email"),
    (Enums.RESEND_OTP_EMAIL.value, "resend_otp_email"),
    (Enums.RESET_PASSWORD_EMAIL.value, "reset_password_email"),
    (Enums.API_RESPONSE.value, "api_response"),
)


class Notification(BaseModel):
    email = models.EmailField()
    event_type = models.PositiveSmallIntegerField(choices=event_type_choices)
    message = models.PositiveSmallIntegerField(choices=event_message_choices)
    is_sent = models.BooleanField(default=False)
    api_response = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-id"]
