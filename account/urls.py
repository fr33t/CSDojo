from django.urls import path
from account.views import manage, auth, profile

urlpatterns = [
    path("register", manage.register, name="注册"),
    path("recover", manage.recover, name="找回"),
    #
    path("login_pw", auth.login_with_password, name="密码登录"),
    path("login_tp", auth.login_with_totp_code, name="TOTP登录"),
    #
    path("profile", profile.profile, name="个人资料"),
]
