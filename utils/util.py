# -*- coding: utf-8 -*-
import secrets


def response_data_formating(generalMessage, data, error=None):
    response_data = {
        "message": generalMessage,
        "error": error,
        "data": data,
    }
    return response_data


def generate_otp():
    digits = "0123456789"
    otp = "".join(secrets.choice(digits) for _ in range(4))
    return otp
