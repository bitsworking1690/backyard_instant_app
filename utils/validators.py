# -*- coding: utf-8 -*-
import re


def custom_password_validator(password):

    # Password should be alphanumeric with at least one special character having length b/w 8-15
    regex = r"^(?=.{8,15})(?=.*[a-z])(?=.*[A-Z])(?=.*[{}():;,.?|_`~%/\-*@#$%^&+=!]).*$"
    g = re.compile(regex)

    # Password should not contain more than 3 repeated characters consecutively
    if re.search(r"(.)\1{3,}", password):
        return False
    if re.fullmatch(g, password):
        return True
    return False
