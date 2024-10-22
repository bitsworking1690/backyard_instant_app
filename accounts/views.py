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
)
from accounts.services import AccountService
from utils.util import response_data_formating
from rest_framework.views import APIView
import ast
from rest_framework.permissions import IsAuthenticated
from utils.error import APIError, Error


class RegularTokenObtainPairView(TokenObtainPairView):
    authentication_classes = []
    serializer_class = RegularTokenObtainPairSerializer
    queryset = CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(email=request.data["email"])
        except CustomUser.DoesNotExist:
            raise APIError(
                Error.INVALID_JWT_TOKEN, extra=["The information provided is incorrect"]
            )
        
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


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

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
                Error.INVALID_JWT_TOKEN, extra=[f"Invalid token {error}"]
            )


class VerifyOtpView(APIView):
    authentication_classes = []

    def post(self, request):
        data = {}
        serializer = CheckOTPSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data
            user = AccountService.checkUserExist(data)
            AccountService.verify_otp_email(data)

            if data["token"] != str(user.token):
                raise APIError(Error.DEFAULT_ERROR, extra=["Token not valid"])

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
