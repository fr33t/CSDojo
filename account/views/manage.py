# ruff: noqa: F403, F401, F405
from . import *


from django.db.utils import IntegrityError
from account.models import User


@require_POST
@require_json_content_type
@validate_request_data_json_decorator(["email", "password", "nickname"])
def register(request: HttpRequest) -> JsonResponse:
    """注册"""
    data = request.vdata

    new_user = User()
    new_user.nickname = data["nickname"]
    new_user.email = data["email"]
    new_user.password_hash = PasswordHasher().hash(data["password"])

    totp = pyotp.TOTP(pyotp.random_base32())
    new_user.totp_uri = totp.provisioning_uri(name=data["email"], issuer_name="CSDojo")
    try:
        new_user.save()
    except IntegrityError:
        return JsonResponse({"message": "已被注册", "code": "200"})

    return JsonResponse({"totp_uri": new_user.totp_uri, "code": "200"})


@require_POST
@require_json_content_type
@validate_request_data_json_decorator(["email"])
def recover(request: HttpRequest):
    """恢复账户"""
    # data = request.vdata
    # users = User.objects.filter(email=data["email"])
    # if len(users) != 0:
    #     user = users[0]
    #     subject = "您的2FA验证码， 请添加后尽快删除邮件"
    #     mail_msg = f"""<img src="https://api.qrtool.cn/?text={user.totp_uri}">"""
    #     if not send_email(data["email"], subject, mail_msg):
    #         return JsonResponse({"message": "发送失败"}, status=500)

    return JsonResponse(
        {
            "message": "已发送TOTP二维码到您的邮箱, 若没有， 请检查垃圾箱或稍候重试",
            "code": "200",
        }
    )
