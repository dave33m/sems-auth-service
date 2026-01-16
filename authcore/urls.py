from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("login/", views.LoginView.as_view(), name="auth-login"),
    path("GetToken/", views.ClientTokenView.as_view(), name="client-token"),
    path("clients/", views.CreateClientView.as_view(), name="create-client"),
    path("refresh/", views.RefreshView.as_view(), name="auth-refresh"),
    path("logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("logout-all/", views.LogoutAllView.as_view(), name="auth-logout-all"),
    path ("forgot-password/", views.ForgotPasswordView.as_view(), name = "auth-forgot-password"),
    path ("reset-password/", views.ResetPasswordView.as_view(), name = "auth-reset-password"),
    path("change-password/", views.ChangePasswordView.as_view(), name="auth-change-password"),
    path("verify-otp/", views.VerifyOtpView.as_view(), name = "auth-verify-otp")
]