# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import CustomUser, EmailOtp
from django.conf import settings
from utils.enums import Enums


@pytest.mark.django_db
class TestSignUpView:
    """
    Test cases for the SignUpView.
    """

    def test_signup_success(self, client, mock_send_otp_email):
        """
        Test successful user sign-up should return 200 OK.
        """
        url = reverse("signup")
        data = {
            "email": "test_signup@gmail.com",
            "password": "Hello@123",
            "password2": "Hello@123",
            "first_name": "Test",
            "last_name": "User",
            "gender": 1,
        }
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "success"
        assert (
            response.json()["data"]["message"]
            == "OTP has been sent to your registered account"
        )
        assert response.json()["data"]["otp_time"] == settings.RESEND_OTP_TIME

    def test_signup_error(self, client):
        """
        Test sign-up with an invalid/missing data should return 400 BAD REQUEST.
        """
        url = reverse("signup")
        data = {
            "email": "invalid-email",
            "password": "Hello@123",
            "password2": "Hello@123",
            "first_name": "Test",
            "gender": 1,
        }
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["email"] == ["Enter a valid email address."]
        assert response.json()["last_name"] == ["This field is required."]

    def test_signup_password_mismatch(self, client):
        """
        Test sign-up with mismatched passwords should return 400 BAD REQUEST.
        """
        url = reverse("signup")
        data = {
            "email": "test_signup@gmail.com",
            "password": "Hello@123",
            "password2": "Hello@456",
            "first_name": "Test",
            "last_name": "User",
            "gender": 1,
        }
        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["password"] == ["Passwords must match."]


@pytest.mark.django_db
class TestVerifyOtpView:
    """
    Test cases for the VerifyOtpView.
    """

    def setup_method(self):
        """
        Set up method to create instances for testing.
        """

        self.user = CustomUser.objects.create(email="test+1@gmail.com")
        self.email_otp = EmailOtp.objects.create(
            email=self.user.email, otp="1234", stage=Enums.LOGIN.value
        )

    def test_verify_otp_success(self, client, mock_send_otp_email):
        """
        Test successful OTP verification should return 200 OK.
        """
        user = self.user
        url = reverse("verify-otp")
        data = {"otp": "1234", "email": user.email, "token": user.token}
        response = client.post(url, data, content_type="application/json")
        email_otp_obj = EmailOtp.objects.get(email=user.email)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "success"
        assert email_otp_obj.is_valid is True
        assert response.json()["data"]["otp"] == email_otp_obj.otp
        assert response.json()["data"]["email"] == email_otp_obj.email

    def test_verify_otp_error(self, client):
        """
        Test OTP verification with missing token should return 400 BAD REQUEST.
        """
        url = reverse("verify-otp")
        data = {"otp": "1234", "email": "test@gmail.com"}
        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "error"
        assert response.json()["error"]["token"] == ["This field is required."]

    def test_verify_otp_invalid_token(self, client):
        """
        Test OTP verification with an invalid token should return 400 BAD REQUEST.
        """
        user = self.user
        url = reverse("verify-otp")
        data = {
            "otp": "1234",
            "email": user.email,
            "token": "09ab2e2b-5961-46fb-8f47-11155bd2297c",
        }
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "error"
        assert response.json()["error"] == ["Token not valid"]


@pytest.mark.django_db
class TestResendOTPView:
    """
    Test cases for the ResendOTPView.
    """

    def setup_method(self):
        """
        Set up method to create instances for testing.
        """

        self.user = CustomUser.objects.create(email="test+1@gmail.com")

    def test_resend_otp_success(self, client, mock_send_otp_email):
        """
        Test successful OTP resend should return 200 OK.
        """
        user = self.user
        url = reverse("resend-otp")
        data = {"email": user.email, "token": user.token}
        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert (
            response.json()["data"]["message"]
            == "OTP has been sent to your registered account"
        )

    def test_resend_otp_error(self, client):
        """
        Test resend OTP with invalid data should return 400 BAD REQUEST.
        """
        url = reverse("resend-otp")
        data = {"email": "invalid-email", "token": "some_token"}
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "error"
        assert response.json()["error"][0]["email"] == ["Enter a valid email address."]
        assert response.json()["error"][0]["token"] == ["Must be a valid UUID."]


@pytest.mark.django_db
class TestProfileView:
    """
    Test cases for the ProfileView.
    """

    def setup_method(self):
        """
        Set up method to create an instance of User for testing.
        """

        self.user = CustomUser.objects.create(email="test+1@gmail.com")

    def test_get_profile_success(self, client, user_login):
        """
        Test retrieving user profile should return 200 OK.
        """

        user = user_login.get("user")
        url = reverse("user-profile", args=[user.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "success"
        assert response.json()["data"]["email"] == "test@gmail.com"
        assert response.json()["data"]["first_name"] == "test"
        assert response.json()["data"]["last_name"] == "user"

    def test_get_profile_error(self, client, user_login):
        """
        Test retrieving user profile should return 403 FORBIDDEN.
        """

        url = reverse("user-profile", args=[self.user.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.json()["detail"]
            == "You do not have permission to perform this action."
        )

    def test_update_profile_success(self, client, user_login):
        """
        Test updating user profile should return 200 OK.
        """

        user = user_login.get("user")
        url = reverse("user-profile", args=[user.id])
        data = {"first_name": "Updated Name"}
        response = client.put(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "success"
        assert (
            response.json()["data"]["first_name"]
            == CustomUser.objects.get(id=user.id).first_name
        )

    def test_update_profile_error(self, client, user_login):
        """
        Test updating user profile should return 400 BAD REQUEST.
        """

        user = user_login.get("user")
        url = reverse("user-profile", args=[user.id])
        data = {"gender": 3}
        response = client.put(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "error"
        assert response.json()["error"]["gender"][0] == '"3" is not a valid choice.'

    def test_user_profile_not_exist(self, client, user_login):
        """
        Test updating user profile should return 400 BAD REQUEST.
        """

        user_login.get("user")
        url = reverse("user-profile", args=[1000000000])
        response = client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "error"
        assert response.json()["error"] == ["User not Exist"]
