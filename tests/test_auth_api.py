# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import CustomUser
from django_rest_passwordreset.models import ResetPasswordToken


@pytest.mark.django_db
class TestGetTokenDetailsView:
    """
    Test cases for the GetTokenDetailsView.
    """

    def test_get_token_details(self, client, user_login):
        """
        Test retrieving token details should return 200 OK.
        """

        url = reverse("get_token_details")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "success"
        assert response.json()["data"]["token_type"] == "access"


@pytest.mark.django_db
class TestLogoutView:
    """
    Test cases for the LogoutView.
    """

    def test_get_logout_user(self, client, user_login_with_2fa):
        """
        Test user logout should return 200 OK.
        """

        url = reverse("logout")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "success"
        assert response.json()["data"][0] == "You have been Successfully logged out"


@pytest.mark.django_db
class TestPasswordResetEndpoints:
    """
    Test cases for the Password Reset endpoints.
    """

    def setup_method(self):
        """
        Set up method to create a user for password reset tests.
        """

        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="initialPassword123"
        )
        self.reset_password_token = ResetPasswordToken.objects.create(
            user=self.user, key="mock-valid-token"
        )

    def test_reset_password_request_valid_email(
        self, client, mock_send_reset_password_email
    ):
        """
        Test requesting a password reset token with a valid email should return 200 OK.
        """

        data = {"email": self.user.email}
        url = reverse("password_reset")
        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "OK"

    def test_reset_password_request_invalid_email(self, client):
        """
        Test requesting a password reset with an invalid email should return 400 Bad Request.
        """

        data = {"email": "nonexistent@example.com"}
        url = reverse("password_reset")
        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["email"] == [
            "We couldn't find an account associated with that email. Please try a different e-mail address."
        ]

    def test_reset_password_confirm_valid_token(self, client):
        """
        Test confirming a password reset with a valid token should return 200 OK.
        """

        token = "mock-valid-token"
        self.user.set_password("newSecurePassword123")
        self.user.save()

        data = {
            "token": token,
            "password": "newSecurePassword123",
        }
        url = reverse("password_reset_confirm")
        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "OK"

    def test_reset_password_confirm_invalid_token(self, client):
        """
        Test confirming a password reset with an invalid token should return 400 Bad Request.
        """

        data = {
            "token": "invalid-token",
            "password": "newSecurePassword123",
        }
        url = reverse("password_reset_confirm")
        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert (
            response.json()["detail"]
            == "The OTP password entered is not valid. Please check and try again."
        )
