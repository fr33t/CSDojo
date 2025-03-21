from django.urls import path
from . import views

urlpatterns = [
    path("register", views.register),
    path("login_pw", views.login_with_password),
    path("login_tp", views.login_with_totp_code),
    path("test_token", views.test_token),
    path("recover", views.recover),
    path("profile", views.profile),
]
