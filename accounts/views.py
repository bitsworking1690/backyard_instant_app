import uuid
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from cryptography.fernet import Fernet
from rest_framework import generics
from accounts.models import CustomUser, BlacklistedToken
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
        response = super().post(request, *args, **kwargs)
        user = CustomUser.objects.get(email=request.data["email"])
        user.token = str(uuid.uuid4())
        user.save()

        if user.role.filter(name="2fa").exists():
            data = AccountService.sendOTPEmail(user)
            data["token"] = user.token
            return Response(
                data=response_data_formating(
                    generalMessage="success", 
                    data=data
                ),
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
        }
    )
    @transaction.atomic
    @method_decorator(require_json_content_type)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = {
            'message': "OTP has been sent to your registered account",
            'otp_time': settings.RESEND_OTP_TIME,
            'token': user.token
        }
        return Response(
            data=response_data_formating(
                generalMessage="success", 
                data=data
            ),
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
            raise APIError(
                Error.DEFAULT_ERROR, extra=[f"Invalid token {error}"]
            )


class VerifyOtpView(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        request_body=CheckOTPSerializer,
        responses={
            200: openapi.Response("Successful response", CheckOTPSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        }
    )
    @transaction.atomic
    @method_decorator(require_json_content_type)
    def post(self, request):
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
        }
    )
    @transaction.atomic
    @method_decorator(require_json_content_type)
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            AccountService.resend_OTP(serializer.data)
        else:
            raise APIError(Error.DEFAULT_ERROR, extra=[serializer.errors])

        data = {}
        data["message"] = "OTP has been sent to your registered account"

        return Response(
            data=response_data_formating(
                generalMessage="success", 
                data=data
            ),
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
        }
    )
    @method_decorator(require_json_content_type)
    @transaction.atomic
    def put(self, request, pk):
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
        try:
            jwt_token = request.COOKIES.get("access")
            hashed_key = Fernet(settings.HASHED_ACCESS_TOKEN_KEY)
            hashed_token = hashed_key.decrypt(ast.literal_eval(jwt_token))
            token = hashed_token.decode()
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            data = response_data_formating(generalMessage="success", data=payload)
        except Exception:
            raise APIError(
                Error.DEFAULT_ERROR, extra=["Invalid or expired token"]
            )

        return Response(data=data, status=status.HTTP_200_OK)
