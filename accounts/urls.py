# -*- coding: utf-8 -*-
from django.urls import path
from accounts.views import (
    SignUpView,
    VerifyOtpView,
    ResendOTPView,
    ProfileView,
    ModuleListCreateView,
    ModuleDetailView,
    PermissionListCreateView,
    PermissionDetailView,
    RoleListCreateView,
    RoleDetailView,
    UserRoleAssignmentView,
    UserListView,
)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("verify-otp/", VerifyOtpView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("profile/<int:pk>/", ProfileView.as_view(), name="user-profile"),
    path("modules/", ModuleListCreateView.as_view(), name="module-list-create"),
    path("modules/<int:pk>/", ModuleDetailView.as_view(), name="module-detail"),
    path(
        "permissions/",
        PermissionListCreateView.as_view(),
        name="permission-list-create",
    ),
    path(
        "permissions/<int:pk>/",
        PermissionDetailView.as_view(),
        name="permission-detail",
    ),
    path("roles/", RoleListCreateView.as_view(), name="role-list-create"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    path(
        "users/<int:pk>/roles/",
        UserRoleAssignmentView.as_view(),
        name="user-role-assign-remove",
    ),
    path("users-with-roles/", UserListView.as_view(), name="user-list-with-roles"),
]
