# ruff: noqa: F403, F401, F405
from . import *

from argon2.exceptions import VerifyMismatchError


@require_POST
@require_json_content_type
@validate_request_data_json_decorator(["email", "password"])
def login_with_password(request: HttpRequest):
    """密码登录校验"""
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
    """TOTP CODE 登录校验"""
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
