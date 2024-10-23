# -*- coding: utf-8 -*-
from rest_framework_simplejwt import authentication as jwt_authentication
from django.conf import settings
from cryptography.fernet import Fernet
import ast
from utils.error import APIError, Error
from accounts.models import BlacklistedToken


class CustomAuthentication(jwt_authentication.JWTAuthentication):
    def getRequestHeaders(self, string, request):
        if request.headers:
            if string in request.headers:
                return request.headers[string]
            else:
                return False
        else:
            return None

    def authenticate(self, request):
        header = self.get_header(request)
        hashed_key = Fernet(settings.HASHED_ACCESS_TOKEN_KEY)

        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            hashed_token = hashed_key.decrypt(ast.literal_eval(raw_token))
        except Exception:
            raise APIError(Error.DEFAULT_ERROR, extra=["Invalid token"])

        token = hashed_token.decode()
        if BlacklistedToken.objects.filter(token=token).exists():
            raise APIError(Error.DEFAULT_ERROR, extra=["Token is blacklisted"])
        validated_token = self.get_validated_token(token)

        return self.get_user(validated_token), validated_token
