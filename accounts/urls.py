from django.urls import path
from accounts.views import (
    SignUpView,
    VerifyOtpView,
    ResendOTPView,
    ProfileView,
)


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("verify-otp/",VerifyOtpView.as_view(),name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path('profile/<int:pk>/', ProfileView.as_view(), name='user-profile'),
]
