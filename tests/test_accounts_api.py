# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import CustomUser, EmailOtp, Module, Permission, Role
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


@pytest.mark.django_db
class TestModuleEndpoints:
    """
    Test cases for the Module endpoints.
    """

    def setup_method(self):
        """
        Set up method to create instances for testing.
        """

        self.module = Module.objects.create(name="Test Module")

    def test_get_module_list(self, client, user_login):
        """
        Test retrieving module list should return 200 OK.
        """

        url = reverse("module-list-create")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_module(self, client, user_login):
        """
        Test to create module obj should return 201 Created.
        """

        url = reverse("module-list-create")
        data = {"name": "Test Module 2"}
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "test module 2"

    def test_get_module_detail(self, client, user_login):
        """
        Test to get module obj should return 200 OK.
        """

        url = reverse("module-detail", args=[self.module.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == self.module.name

    def test_update_module(self, client, user_login):
        """
        Test to update module obj should return 200 OK.
        """

        url = reverse("module-detail", args=[self.module.id])
        data = {"name": "Updated Module"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "updated module"

    def test_delete_module(self, client, user_login):
        """
        Test to delete module obj should return 204 No Content.
        """

        url = reverse("module-detail", args=[self.module.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestPermissionEndpoints:
    """
    Test cases for the Permission endpoints.
    """

    def setup_method(self):
        """
        Set up method to create instances for testing.
        """

        self.module = Module.objects.create(name="Test Module")
        self.permission = Permission.objects.create(name="can_view", module=self.module)

    def test_get_permission_list(self, client, user_login):
        """
        Test retrieving permission list should return 200 OK.
        """

        url = reverse("permission-list-create")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_permission(self, client, user_login):
        """
        Test to create permission obj should return 201 Created.
        """

        url = reverse("permission-list-create")
        data = {"name": "Test Permission", "module": self.module.id}
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "test permission"
        assert response.json()["module"] == self.module.id

    def test_get_permission_detail(self, client, user_login):
        """
        Test to get permission obj should return 200 OK.
        """

        url = reverse("permission-detail", args=[self.permission.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == self.permission.name

    def test_update_permission(self, client, user_login):
        """
        Test to update permission obj should return 200 OK.
        """

        url = reverse("permission-detail", args=[self.permission.id])
        data = {"name": "Updated Permission", "module": self.module.id}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "updated permission"

    def test_delete_permission(self, client, user_login):
        """
        Test to delete permission obj should return 204 No Content.
        """

        url = reverse("permission-detail", args=[self.permission.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestRoleEndpoints:
    """
    Test cases for the Role endpoints.
    """

    def setup_method(self):
        """
        Set up method to create instances for testing.
        """

        self.role = Role.objects.create(name="Test Role")
        self.module = Module.objects.create(name="Test Module")
        self.permission1 = Permission.objects.create(
            name="can_view", module=self.module
        )
        self.permission2 = Permission.objects.create(name="can_add", module=self.module)

    def test_get_role_list(self, client, user_login):
        """
        Test retrieving role list should return 200 OK.
        """

        url = reverse("role-list-create")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_role(self, client, user_login):
        """
        Test to create role obj should return 201 Created.
        """

        url = reverse("role-list-create")
        data = {
            "name": "Test Role 2",
            "permissions_ids": [self.permission1.id, self.permission2.id],
        }
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "test role 2"

    def test_get_role_detail(self, client, user_login):
        """
        Test to get role obj should return 200 OK.
        """

        url = reverse("role-detail", args=[self.role.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == self.role.name

    def test_update_role(self, client, user_login):
        """
        Test to update role obj should return 200 OK.
        """

        url = reverse("role-detail", args=[self.role.id])
        data = {"name": "Updated Role", "permissions_ids": [self.permission2.id]}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "updated role"

    def test_delete_role(self, client, user_login):
        """
        Test to delete role obj should return 204 No Content.
        """

        url = reverse("role-detail", args=[self.role.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestUserRoleAssignmentEndpoints:
    """
    Test cases for the User Role Assignment endpoint.
    """

    def setup_method(self):
        """
        Set up method to create instances for testing.
        """

        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )
        self.role1 = Role.objects.create(name="Admin")
        self.role2 = Role.objects.create(name="Editor")

    def test_assign_roles_to_user(self, client, user_login):
        """
        Test assigning roles to a user should return 200 OK.
        """

        data = {"role": [self.role1.id, self.role2.id]}
        url = reverse("user-role-assign-remove", args=[self.user.id])
        response = client.put(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]["role"]) == 2

    def test_remove_all_roles_from_user(self, client, user_login):
        """
        Test removing all roles from a user should return 200 OK.
        """

        self.user.role.set([self.role1, self.role2])
        data = {"role": []}
        url = reverse("user-role-assign-remove", args=[self.user.id])
        response = client.put(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]["role"]) == 0

    def test_assign_roles_missing_field(self, client, user_login):
        """
        Test assigning roles with missing role field should return 400 Bad Request.
        """

        url = reverse("user-role-assign-remove", args=[self.user.id])
        response = client.put(url, {}, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["role"] == "This field is required."

    def test_assign_roles_user_not_found(self, client, user_login):
        """
        Test assigning roles to a non-existent user should return 400 Bad Request.
        """

        url = reverse("user-role-assign-remove", args=[999])
        data = {"role": [self.role1.id]}
        response = client.put(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User not Exist" in response.json()["error"]


@pytest.mark.django_db
class TestUserListEndpoints:
    """
    Test cases for the User List endpoint.
    """

    def setup_method(self):
        """
        Set up method to create instances for testing.
        """
        self.user1 = CustomUser.objects.create_user(
            email="user1@example.com",
            password="password1",
            first_name="User",
            last_name="One",
        )
        self.user2 = CustomUser.objects.create_user(
            email="user2@example.com",
            password="password2",
            first_name="User",
            last_name="Two",
        )
        self.role1 = Role.objects.create(name="Admin")
        self.role2 = Role.objects.create(name="Viewer")
        self.user1.role.add(self.role1)
        self.user2.role.add(self.role2)

    def test_get_user_list(self, client, user_login):
        """
        Test retrieving the user list should return 200 OK.
        """
        url = reverse("user-list-with-roles")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"][1]["email"] == "user2@example.com"
        assert response.json()["data"][2]["email"] == "user1@example.com"
        assert response.json()["data"][1]["roles"][0]["name"] == "viewer"
        assert response.json()["data"][2]["roles"][0]["name"] == "admin"
