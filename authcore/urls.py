from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("login/", views.LoginView.as_view(), name="auth-login"),
    path("oauth/token", views.ClientTokenView.as_view(), name="client-token"),
    path("clients", views.CreateClientView.as_view(), name="create-client"),
]