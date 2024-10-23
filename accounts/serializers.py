# -*- coding: utf-8 -*-
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from accounts.models import CustomUser
from accounts.services import AccountService
from utils.serializers import CustomBaseModelSerializer, CustomBaseSerializer


class RegularTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token


class CustomUserCreateSerializer(CustomBaseModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "password", "password2", "first_name", "last_name", "gender"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            gender=validated_data["gender"],
        )
        user.set_password(validated_data["password"])
        user.is_active = False
        user.save()
        _ = AccountService.sendOTPEmail(user)

        return user


class CheckOTPSerializer(CustomBaseSerializer):
    otp = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    token = serializers.UUIDField(required=True)


class ResendOTPSerializer(CustomBaseSerializer):
    email = serializers.EmailField(required=True)
    token = serializers.UUIDField(required=True)


class ProfileSerializer(CustomBaseModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "gender", "role"]
        read_only_fields = ["email"]


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.DictField()


class SignUpResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    otp_time = serializers.CharField()
    token = serializers.UUIDField()


class ResendOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
