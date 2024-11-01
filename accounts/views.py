# -*- coding: utf-8 -*-
import uuid
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from cryptography.fernet import Fernet
from rest_framework import generics
from accounts.models import CustomUser, BlacklistedToken, Role, Permission, Module
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import (
    RegularTokenObtainPairSerializer,
    CustomUserCreateSerializer,
    CheckOTPSerializer,
    ResendOTPSerializer,
    ProfileSerializer,
    ErrorResponseSerializer,
    SignUpResponseSerializer,
    ResendOTPResponseSerializer,
    ModuleSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserRoleAssignmentSerializer,
    UserListSerializer,
)
from accounts.services import AccountService
from utils.util import response_data_formating
from rest_framework.views import APIView
import ast
import jwt
from rest_framework.permissions import IsAuthenticated
from utils.error import APIError, Error
from django.db import transaction
from accounts.permissions import IsOwner
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from utils.decorators import require_json_content_type
from django.utils.decorators import method_decorator


class RegularTokenObtainPairView(TokenObtainPairView):
    authentication_classes = []
    serializer_class = RegularTokenObtainPairSerializer
    queryset = CustomUser.objects.all()

    @transaction.atomic
    @method_decorator(require_json_content_type)
    def post(self, request, *args, **kwargs):
        """Handle user login and token generation.

        This method overrides the default `post` method to:
        1. Retrieve the user by their email.
        2. Assign a new token to the user.
        3. Check if the user has the 2FA role. If so, it sends an OTP email and returns the response.
        4. Encrypt the access token and store it in a secure HTTP-only cookie.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The HTTP response with a JWT token or 2FA OTP data.

        Raises:
            CustomUser.DoesNotExist: If the user with the given email does not exist.
        """

        response = super().post(request, *args, **kwargs)
        user = CustomUser.objects.get(email=request.data["email"])
        user.token = str(uuid.uuid4())
        user.save()

        if user.role.filter(name="2fa").exists():
            data = AccountService.sendOTPEmail(user)
            data["token"] = user.token
            return Response(
                data=response_data_formating(generalMessage="success", data=data),
                status=status.HTTP_200_OK,
            )

        hashed_key = Fernet(settings.HASHED_ACCESS_TOKEN_KEY)
        access_token = hashed_key.encrypt(response.data["access"].encode())

        if response.status_code == 200:
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=access_token,
                expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )

        return response


class SignUpView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer

    @swagger_auto_schema(
        request_body=CustomUserCreateSerializer,
        responses={
            201: openapi.Response("Successful response", SignUpResponseSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @transaction.atomic
    @method_decorator(require_json_content_type)
    def post(self, request, *args, **kwargs):
        """Handle user sign-up and OTP generation.

        This method handles the user sign-up process. It validates the incoming request
        data using the `CustomUserCreateSerializer`, saves the user data, and generates
        an OTP. The OTP is sent to the user's registered email address.

        Args:
            request (HttpRequest): The HTTP request object containing user data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A response object containing a success message, OTP resend time,
            and a unique token for the user.

        Raises:
            ValidationError: If the serializer data is invalid.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = {
            "message": "OTP has been sent to your registered account",
            "otp_time": settings.RESEND_OTP_TIME,
            "token": user.token,
        }
        return Response(
            data=response_data_formating(generalMessage="success", data=data),
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful logout"),
            401: openapi.Response("Unauthorized"),
        }
    )
    def get(self, request):
        """
        Handle the logout process by clearing the user's authentication cookie and blacklisting the JWT token.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: A success response confirming the logout process, with the JWT token blacklisted.

        Raises:
            APIError: If an invalid or expired token is encountered during the process.
        """

        try:
            response = Response(
                response_data_formating(
                    generalMessage="success",
                    data=["You have been Successfully logged out"],
                )
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                expires="Thu, 01 Jan 1970 00:00:00 GMT",
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )

            jwt_token = request.COOKIES.get("access")
            hashed_key = Fernet(settings.HASHED_ACCESS_TOKEN_KEY)
            hashed_token = hashed_key.decrypt(ast.literal_eval(jwt_token))
            token = hashed_token.decode()
            BlacklistedToken.objects.create(token=token)
            return response
        except Exception as error:
            raise APIError(Error.DEFAULT_ERROR, extra=[f"Invalid token {error}"])


class VerifyOtpView(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        request_body=CheckOTPSerializer,
        responses={
            200: openapi.Response("Successful response", CheckOTPSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @transaction.atomic
    @method_decorator(require_json_content_type)
    def post(self, request):
        """
        Verify the user's OTP and activate the account if the OTP and token are valid.

        Args:
            request (HttpRequest): The HTTP request object containing OTP and token data.

        Returns:
            Response: A success response with a new access token if the OTP is verified.
            If the OTP verification fails, a 400 response is returned with error details.

        Raises:
            APIError: If the token provided is invalid or if any other validation errors occur.
        """

        data = {}
        serializer = CheckOTPSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data
            user = AccountService.checkUserExist(data)
            AccountService.verify_otp_email(data, user)

            if data["token"] != str(user.token):
                raise APIError(Error.DEFAULT_ERROR, extra=["Token not valid"])

            if not user.is_active:
                user.is_active = True
                user.save()

            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            hashed_key = Fernet(settings.HASHED_ACCESS_TOKEN_KEY)
            access_token = hashed_key.encrypt(access.encode())
        else:
            return Response(
                response_data_formating(
                    generalMessage="error", error=serializer.errors, data=None
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(
            response_data_formating(generalMessage="success", data=data),
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access_token,
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )

        return response


class ResendOTPView(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        request_body=ResendOTPSerializer,
        responses={
            200: openapi.Response("Successful response", ResendOTPResponseSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @transaction.atomic
    @method_decorator(require_json_content_type)
    def post(self, request):
        """
        Resend an OTP to the user's registered account if requested.

        Args:
            request (HttpRequest): The HTTP request object containing user data.

        Returns:
            Response: A success response indicating that the OTP has been sent to the user's email.

        Raises:
            APIError: If there are validation errors in the user data.
        """

        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            AccountService.resend_OTP(serializer.data)
        else:
            raise APIError(Error.DEFAULT_ERROR, extra=[serializer.errors])

        data = {}
        data["message"] = "OTP has been sent to your registered account"

        return Response(
            data=response_data_formating(generalMessage="success", data=data),
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [IsOwner]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise APIError(Error.DEFAULT_ERROR, extra=["User not Exist"])

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", ProfileSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
            403: openapi.Response("Forbidden"),
        }
    )
    def get(self, request, pk):
        """
        Retrieve the profile details of a user based on their ID (pk).

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The primary key (ID) of the user whose profile is being requested.

        Returns:
            Response: A success response containing the user's profile data.

        Raises:
            APIError: If the user does not exist or the requesting user does not have permission.
        """

        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        serializer = ProfileSerializer(user)
        return Response(
            response_data_formating(generalMessage="success", data=serializer.data),
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        request_body=ProfileSerializer,
        responses={
            200: openapi.Response("Successful response", ProfileSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
            403: openapi.Response("Forbidden"),
        },
    )
    @method_decorator(require_json_content_type)
    @transaction.atomic
    def put(self, request, pk):
        """
        Update the profile information of a user based on their ID (pk).

        Args:
            request (HttpRequest): The HTTP request object containing the updated profile data.
            pk (int): The primary key (ID) of the user whose profile is being updated.

        Returns:
            Response: A success response with the updated profile data if the operation is successful.
            A 400 error response if validation fails.

        Raises:
            APIError: If the user does not exist or the requesting user does not have permission.
        """

        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                response_data_formating(generalMessage="success", data=serializer.data)
            )
        return Response(
            response_data_formating(
                generalMessage="error", data=None, error=serializer.errors
            ),
            status=status.HTTP_400_BAD_REQUEST,
        )


class GetTokenDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful retrieval"),
            401: openapi.Response("Unauthorized"),
        }
    )
    def get(self, request):
        """
        Retrieve details of the token stored in the user's cookies.

        Args:
            request (HttpRequest): The HTTP request object containing the access token in cookies.

        Returns:
            Response: A success response with decoded token payload details.

        Raises:
            APIError: If the token is invalid or has expired.
        """

        try:
            jwt_token = request.COOKIES.get("access")
            hashed_key = Fernet(settings.HASHED_ACCESS_TOKEN_KEY)
            hashed_token = hashed_key.decrypt(ast.literal_eval(jwt_token))
            token = hashed_token.decode()
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            data = response_data_formating(generalMessage="success", data=payload)
        except Exception:
            raise APIError(Error.DEFAULT_ERROR, extra=["Invalid or expired token"])

        return Response(data=data, status=status.HTTP_200_OK)


class ModuleListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", ModuleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=ModuleSerializer,
        responses={
            201: openapi.Response("Successful response", ModuleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @method_decorator(require_json_content_type)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", ModuleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=ModuleSerializer,
        responses={
            200: openapi.Response("Successful response", ModuleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @method_decorator(require_json_content_type)
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            204: openapi.Response("Successful response", ModuleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class PermissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", PermissionSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=PermissionSerializer,
        responses={
            201: openapi.Response("Successful response", PermissionSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @method_decorator(require_json_content_type)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", PermissionSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=PermissionSerializer,
        responses={
            200: openapi.Response("Successful response", PermissionSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @method_decorator(require_json_content_type)
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            204: openapi.Response("Successful response", PermissionSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class RoleListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", RoleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=RoleSerializer,
        responses={
            201: openapi.Response("Successful response", RoleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @method_decorator(require_json_content_type)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", RoleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=RoleSerializer,
        responses={
            200: openapi.Response("Successful response", RoleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @method_decorator(require_json_content_type)
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            204: openapi.Response("Successful response", RoleSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class UserRoleAssignmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise APIError(Error.DEFAULT_ERROR, extra=["User not Exist"])

    @swagger_auto_schema(
        request_body=UserRoleAssignmentSerializer,
        responses={
            200: openapi.Response("Successful response", UserRoleAssignmentSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        },
    )
    @method_decorator(require_json_content_type)
    @transaction.atomic
    def put(self, request, pk):
        """
        Update the roles of a specific user.

        Args:
            request (Request): The incoming HTTP request.
            pk (int): Primary key of the user to update.

        Returns:
            Response: The HTTP response with success or error message.
        """

        user = self.get_object(pk)
        serializer = UserRoleAssignmentSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                response_data_formating(generalMessage="success", data=serializer.data)
            )
        return Response(
            response_data_formating(
                generalMessage="error", data=None, error=serializer.errors
            ),
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserListView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", UserListSerializer),
            401: openapi.Response("Unauthorized"),
        },
    )
    def get(self, request):
        """
        Retrieve all users with their associated roles.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: The HTTP response containing a list of users and their roles.
        """

        users = CustomUser.objects.prefetch_related("role").all()
        serializer = UserListSerializer(users, many=True)
        return Response(
            response_data_formating(generalMessage="success", data=serializer.data)
        )
