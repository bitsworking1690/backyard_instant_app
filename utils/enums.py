# -*- coding: utf-8 -*-
from enum import Enum


class Enums(Enum):

    # GENDER_CHOICES
    MALE = 1
    FEMALE = 2

    # OTP_STAGES
    SIGN_UP = 1
    LOGIN = 2

    # Notification Even Type Choices
    EMAIL = 1
    WHATSAPP = 2
    SMS = 3
    API = 4

    # Notification Even Message Choices
    SIGN_UP_OTP_EMAIL = 1
    LOGIN_OTP_EMAIL = 2
    RESEND_OTP_EMAIL = 3
    RESET_PASSWORD_EMAIL = 4
    API_RESPONSE = 5
