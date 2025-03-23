from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest
import functools
import json
import jwt
import smtplib
from functools import wraps
from . import settings
import datetime
import uuid
import docker

docker_client = docker.from_env()


def require_json_content_type(view_func):
    @functools.wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.content_type != "application/json":
            return JsonResponse(
                {"error": "Content-Type must be application/json"}, status=400
            )
        return view_func(request, *args, **kwargs)

    return wrapper


def validate_request_data_json_decorator(required_fields):
    """
    装饰器：验证请求体中的 JSON 数据是否包含必需的字段。
    :param required_fields: 必需字段的列表，例如 ["email", "password", "nickname"]
    :return: 如果验证失败，返回 HttpResponseBadRequest；否则继续执行视图函数
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # 解析请求体中的 JSON 数据
                data = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return HttpResponseBadRequest("Invalid JSON data")

            # 检查必需的字段是否存在且不为空
            if not all(field in data and data[field] for field in required_fields):
                return HttpResponseBadRequest("Missing or empty required fields")

            # 将解析后的数据添加到 request 对象中
            request.vdata = data

            # 调用视图函数
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def jwt_required(view_func):
    """
    装饰器：验证 JWT Token
    """

    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_jwt_token(token)
                if payload:
                    # 将用户信息添加到 request 对象中
                    request.jdata = payload
                    return view_func(request, *args, **kwargs)
            except jwt.ExpiredSignatureError or Exception:
                return JsonResponse({"message": "未登录", "code": "401"})

        # 如果 Token 无效，返回 401 Unauthorized
        return JsonResponse({"message": "未登录", "code": "401"})

    return wrapper


def generate_jwt_token(data, expires_in=8 * 60 * 60) -> str:
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    data = {**data, "exp": exp_time}
    return jwt.encode(data, key=settings.JWT_SECRET, algorithm="HS256")


def decode_jwt_token(token):
    return jwt.decode(token, key=settings.JWT_SECRET, algorithms="HS256")


def send_email(receiver, subject, msg) -> bool:
    from email.mime.text import MIMEText
    from email.header import Header

    receivers = [receiver]
    message = MIMEText(msg, "html", "utf-8")
    message["From"] = Header(settings.SMTP_ACCOUNT, "utf-8")
    message["To"] = Header(receiver, "utf-8")

    message["Subject"] = Header(subject, "utf-8")

    try:
        smtp = smtplib.SMTP()
        smtp.connect("smtp.163.com", 25)
        smtp.login("freetbash@163.com", "RYg8xGMnQ57Ljh6f")
        smtp.sendmail("freetbash@163.com", receivers, msg)
        return True
    except Exception as e:
        print(e)
        return False


def generate_flag() -> str:
    unique_flag = uuid.uuid4().hex
    return f"flag{{{unique_flag}}}"
