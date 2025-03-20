from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.db.utils import IntegrityError

from CSDojo.utils import (
    require_json_content_type,
    validate_request_data_json_decorator,
    generate_jwt_token,
    jwt_required,
)

import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from .models import User


@require_POST
@require_json_content_type
@validate_request_data_json_decorator(["email", "password", "nickname"])
def register(request: HttpRequest) -> JsonResponse:
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
@validate_request_data_json_decorator(["email", "password"])
def login_with_password(request: HttpRequest):
    data = request.vdata
    users = User.objects.filter(email=data["email"])
    if len(users) == 0:
        return JsonResponse({"message": "邮箱或密码不正确", "code": "400"})

    user = users[0]

    try:
        ph = PasswordHasher()
        ph.verify(user.password_hash, data["password"])
        token = generate_jwt_token({"email": data["email"]})
        return JsonResponse({"token": token, "code": "200"})

    except VerifyMismatchError:
        return JsonResponse({"message": "邮箱或密码不正确", "code": "400"})


@require_POST
@require_json_content_type
@validate_request_data_json_decorator(["email", "totp_code"])
def login_with_totp_code(request: HttpRequest):
    data = request.vdata
    users = User.objects.filter(email=data["email"])
    if len(users) == 0:
        return JsonResponse({"message": "邮箱或密码不正确", "code": "400"})

    user = users[0]

    totp = pyotp.parse_uri(user.totp_uri)
    if totp.verify(data["totp_code"]):
        token = generate_jwt_token({"email": data["email"]})
        return JsonResponse({"token": token, "code": "200"})
    else:
        return JsonResponse({"message": "邮箱或代码不正确", "code": "400"})


@jwt_required
def test_token(request: HttpRequest):
    print(request.jdata)
    return JsonResponse({"message": "ok", "code": "200"})


@require_POST
@require_json_content_type
@validate_request_data_json_decorator(["email"])
def recover(request: HttpRequest):
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
