# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from utils.models import BaseModel

class DataImport(BaseModel):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="data_imports"
    )  # User initiating the import
    file_name = models.CharField(max_length=255)  # Name of the imported file
    file_type = models.CharField(max_length=50)  # Type of the file (e.g., "csv", "json", "xml")
    status = models.CharField(
        max_length=50, 
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ]
    )  # Status of the import
    error_message = models.TextField(blank=True)  # Error details if the import fails
    imported_at = models.DateTimeField(blank=True, null=True)  # Timestamp when the import was completed

    class Meta:
        verbose_name = "Data Import"
        verbose_name_plural = "Data Imports"


class DataExport(BaseModel):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="data_exports"
    )  # User initiating the export
    file_name = models.CharField(max_length=255)  # Name of the exported file
    file_type = models.CharField(max_length=50)  # Type of the file (e.g., "csv", "json", "xml")
    status = models.CharField(
        max_length=50, 
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ]
    )  # Status of the export
    error_message = models.TextField(blank=True)  # Error details if the export fails
    exported_at = models.DateTimeField(blank=True, null=True)  # Timestamp when the export was completed

    class Meta:
        verbose_name = "Data Export"
        verbose_name_plural = "Data Exports"


class DataImportMapping(BaseModel):
    import_instance = models.ForeignKey(
        DataImport, 
        on_delete=models.CASCADE, 
        related_name="mappings"
    )  # Related data import
    source_field = models.CharField(max_length=255)  # Field name in the imported file
    target_field = models.CharField(max_length=255)  # Corresponding field name in the system
    transformation_rules = models.JSONField(blank=True, null=True)  # Rules for transforming the data

    class Meta:
        verbose_name = "Data Import Mapping"
        verbose_name_plural = "Data Import Mappings"


class DataExportMapping(BaseModel):
    export_instance = models.ForeignKey(
        DataExport, 
        on_delete=models.CASCADE, 
        related_name="mappings"
    )  # Related data export
    source_field = models.CharField(max_length=255)  # Field name in the system
    target_field = models.CharField(max_length=255)  # Corresponding field name in the exported file
    transformation_rules = models.JSONField(blank=True, null=True)  # Rules for transforming the data

    class Meta:
        verbose_name = "Data Export Mapping"
        verbose_name_plural = "Data Export Mappings"
