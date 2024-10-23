from django.conf import settings
from accounts.models import EmailOtp, CustomUser
from utils.util import generate_otp
from utils.email import otp_email
from utils.error import APIError, Error
from datetime import timedelta
from django.utils import timezone
from utils.enums import Enums


class AccountService:
    
    @staticmethod
    def sendOTPEmail(user):
        data = {}
        if user.is_active:
            stage = Enums.LOGIN.value
        else:
            stage = Enums.SIGN_UP.value
        otp = EmailOtp(
            email=user.email,
            otp=generate_otp(),
            stage=stage
        )
        otp.save()
        otp_email(user.first_name, user.email, otp.otp)
        
        data['message'] = "OTP has been sent to your registered account"
        data['otp_time'] = settings.RESEND_OTP_TIME
        
        return data

    @staticmethod
    def checkUserExist(data):
        if "email" in data:
            user = CustomUser.objects.filter(
                email=data["email"].lower()
            )
            if not user.exists():
                raise APIError(
                    Error.DEFAULT_ERROR, extra=["The information provided is incorrect"]
                )
            return user.first()
        else:
            raise APIError(Error.DEFAULT_ERROR, extra=["Email is Required"])

    @staticmethod
    def verify_otp_email(data, user):
        if user.is_active:
            stage = Enums.LOGIN.value
        else:
            stage = Enums.SIGN_UP.value
        expiration_period = timedelta(seconds=int(settings.RESEND_OTP_TIME))
        otp_obj = (
            EmailOtp.objects.filter(
                otp=data["otp"], email=data["email"].lower(), is_valid=False, stage=stage
            )
            .order_by("created_at")
            .first()
        )

        if not otp_obj:
            raise APIError(
                Error.DEFAULT_ERROR, extra=["The information provided is incorrect"]
            )

        if otp_obj.created_at < (timezone.now() - expiration_period):
            raise APIError(Error.DEFAULT_ERROR, extra=["OTP has been Expired"])

        otp_obj.is_valid = True
        otp_obj.save()

    @staticmethod
    def resend_OTP(data):
        try:
            user = CustomUser.objects.get(
                email=data["email"].lower(), 
                token=data["token"]
            )
        except CustomUser.DoesNotExist:
            raise APIError(
                Error.DEFAULT_ERROR, extra=["The information provided is incorrect"]
            )

        if user.is_active:
            stage = Enums.LOGIN.value
        else:
            stage = Enums.SIGN_UP.value

        otp = EmailOtp(
            email=user.email,
            otp=generate_otp(),
            stage=stage
        )
        otp.save()
        otp_email(user.first_name, user.email, otp.otp)
