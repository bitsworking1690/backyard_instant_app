# -*- coding: utf-8 -*-
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from accounts.models import CustomUser, Role, Permission, Module
from accounts.services import AccountService
from utils.serializers import CustomBaseModelSerializer, CustomBaseSerializer
from utils.validators import custom_password_validator


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
        if data["email"] == data["password"]:
            raise serializers.ValidationError("Password can not be same as email")
        if not custom_password_validator(data["password"]):
            raise serializers.ValidationError(
                "Length must be between 8 to 15 characters, should not contain more than 3 "
                "repeated characters consecutively, and at least contains one uppercase, lowercase and "
                "special characters."
            )
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


class ModuleSerializer(CustomBaseModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "name"]
        read_only_fields = ["id"]


class PermissionSerializer(CustomBaseModelSerializer):
    module_name = serializers.CharField(source="module.name", read_only=True)

    class Meta:
        model = Permission
        fields = ["id", "name", "module", "module_name"]
        read_only_fields = ["id"]


class RoleSerializer(CustomBaseModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permissions_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        source="permissions",
        many=True,
        write_only=True,
    )

    class Meta:
        model = Role
        fields = ["id", "name", "permissions", "permissions_ids"]
        read_only_fields = ["id"]


class UserRoleAssignmentSerializer(CustomBaseModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)

    class Meta:
        model = CustomUser
        fields = ["role"]

    def update(self, instance, validated_data):
        roles = validated_data.get("role", None)

        if roles is not None:
            if roles:
                instance.role.set(roles)
            else:
                instance.role.clear()
            instance.save()
        else:
            raise serializers.ValidationError({"role": "This field is required."})

        return instance


class UserRoleSerializer(CustomBaseModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class UserListSerializer(CustomBaseModelSerializer):
    roles = UserRoleSerializer(many=True, read_only=True, source="role")

    class Meta:
        model = CustomUser
        fields = ["id", "email", "first_name", "last_name", "roles"]
