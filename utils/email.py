from django.conf import settings
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from rest_framework import status



def otp_email(first_name, email, otp):
    try:
        subject = "OTP Verification"

        plain_message = f"{first_name}: {email}: {otp}"
        from_email = settings.EMAIL_HOST_USER
        to = email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to]
        )
    except Exception as e:
        raise ValidationError(
            detail=f"Error in sending email {e}",
            code=status.HTTP_400_BAD_REQUEST
        )
