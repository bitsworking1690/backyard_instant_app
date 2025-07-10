# Create your models here.
from django.db import models
from utils.models import BaseModel  # Assuming BaseModel includes common fields like `is_deleted`, `created_at`, and `updated_at`

class Form(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="forms_created"
    )

    def __str__(self):
        return self.title


class FieldTypes(models.TextChoices):
    TEXT = "text", "Text"
    NUMBER = "number", "Number"
    DATETIME = "datetime", "Datetime"
    DROPDOWN = "dropdown", "Dropdown"
    CHECKBOX = "checkbox", "Checkbox"
    RADIO = "radio", "Radio"
    FILE = "file", "File"


class FormField(BaseModel):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="fields")
    field_type = models.CharField(max_length=20, choices=FieldTypes.choices)
    label = models.CharField(max_length=255)
    placeholder = models.CharField(max_length=255, blank=True, null=True)
    is_required = models.BooleanField(default=False)
    options = models.JSONField(blank=True, null=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.label} ({self.field_type})"


class FormSubmission(BaseModel):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="submissions")
    submitted_by = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="form_submissions"
    )
    submission_data = models.JSONField()

    def __str__(self):
        return f"Submission for {self.form.title} by {self.submitted_by}"


class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"


class FormAssignment(BaseModel):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="assignments")
    assigned_to = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="form_assignments"
    )
    assigned_by = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="forms_assigned"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f"{self.form.title} assigned to {self.assigned_to}"
