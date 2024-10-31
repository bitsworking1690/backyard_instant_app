# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse
from rest_framework import status


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
