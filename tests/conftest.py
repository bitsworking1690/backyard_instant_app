# -*- coding: utf-8 -*-
import pytest
from accounts.models import CustomUser
from django.urls import reverse
from unittest.mock import patch
from accounts.models import EmailOtp, Role


@pytest.fixture
def mock_send_otp_email():
    """
    Fixture to mock the 'otp_email' function.
    """

    with patch("utils.email.otp_email") as mock:
        yield mock


@pytest.fixture
def mock_send_reset_password_email():
    """
    Fixture to mock the 'reset_password_email' function.
    """

    with patch("utils.email.reset_password_email") as mock:
        yield mock


@pytest.fixture
def user_login(client, mock_send_otp_email):
    """
    Fixture to register and log in a participant user.
    """

    url = reverse("signup")
    data = {
        "email": "test@gmail.com",
        "password": "Hello@123",
        "password2": "Hello@123",
        "first_name": "test",
        "last_name": "user",
        "gender": 1,
    }
    response = client.post(url, data, content_type="application/json")
    user = CustomUser.objects.get(
        email="test@gmail.com", token=response.data["data"]["token"]
    )
    EmailOtp.objects.create(email="test@gmail.com", otp="1234")

    url = reverse("verify-otp")
    data = {
        "email": "test@gmail.com",
        "otp": "1234",
        "token": response.data["data"]["token"],
    }
    response = client.post(url, data, content_type="application/json")

    url = reverse("access_token")
    data = {"email": "test@gmail.com", "password": "Hello@123"}
    response = client.post(url, data, content_type="application/json")

    return {"user_authtoken": f"Bearer {response.json()['access']}", "user": user}


@pytest.fixture
def user_login_with_2fa(client, mock_send_otp_email):
    """
    Fixture to register and log in a participant user.
    """

    url = reverse("signup")
    data = {
        "email": "test@gmail.com",
        "password": "Hello@123",
        "password2": "Hello@123",
        "first_name": "test",
        "last_name": "user",
        "gender": 1,
    }
    response = client.post(url, data, content_type="application/json")
    user = CustomUser.objects.get(
        email="test@gmail.com", token=response.data["data"]["token"]
    )
    role = Role.objects.create(name="2fa")
    user.role.add(role)
    EmailOtp.objects.create(email="test@gmail.com", otp="1234")

    url = reverse("verify-otp")
    data = {
        "email": "test@gmail.com",
        "otp": "1234",
        "token": response.data["data"]["token"],
    }
    response = client.post(url, data, content_type="application/json")

    url = reverse("access_token")
    data = {"email": "test@gmail.com", "password": "Hello@123"}
    response = client.post(url, data, content_type="application/json")

    return {"user": user}
