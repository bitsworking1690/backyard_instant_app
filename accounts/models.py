# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from utils.enums import Enums
from utils.models import BaseModel
import uuid
from simple_history.models import HistoricalRecords


class Module(BaseModel):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super().save(*args, **kwargs)


class Permission(BaseModel):
    name = models.CharField(max_length=64)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "module")
        ordering = ("-id",)

    def __str__(self):
        return f"{self.name} ({self.module.name})"

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super().save(*args, **kwargs)


class Role(BaseModel):
    name = models.CharField(max_length=64, unique=True)
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super().save(*args, **kwargs)
    
class RolePermission(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        constraints = [
        models.UniqueConstraint(fields=["role", "permission"], name="unique_role_permission")
        ]
        ordering = ["-id"]

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    USER_GENDER_CHOICES = ((Enums.MALE.value, "Male"), (Enums.FEMALE.value, "Female"))

    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    gender = models.PositiveSmallIntegerField(
        choices=USER_GENDER_CHOICES, default=Enums.MALE.value
    )
    role = models.ManyToManyField(Role, related_name="users", blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    history = HistoricalRecords()

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"{self.email} - {self.id}"

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        return super().save(*args, **kwargs)


class EmailOtp(BaseModel):
    OTP_STAGES = (
        (Enums.SIGN_UP.value, "Sign Up"),
        (Enums.LOGIN.value, "Login"),
    )

    email = models.EmailField()
    otp = models.CharField(max_length=4)
    is_valid = models.BooleanField(default=False)
    stage = models.PositiveSmallIntegerField(
        choices=OTP_STAGES, default=Enums.SIGN_UP.value
    )

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.otp


class BlacklistedToken(BaseModel):
    token = models.CharField(max_length=1000)

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return str(self.id)
