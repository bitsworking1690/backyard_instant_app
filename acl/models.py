from django.db import models

# Create your models here.
from django.db import models
from utils.models import BaseModel


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
    permissions = models.ManyToManyField(
        Permission, 
        related_name="roles", 
        blank=True
    )  # Establishes a many-to-many relationship between Role and Permission, allowing roles to be associated with multiple permissions. The related_name "roles" enables reverse querying from the Permission model.

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.name


class RolePermission(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_permissions")

    class Meta:
        unique_together = ("role", "permission")
        ordering = ("-id",)

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"