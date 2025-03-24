# ruff: noqa: F403, F401, F405
from . import *


@require_GET
@jwt_required
def tags(request: HttpRequest):
    """所有标签"""
    data = [str(tag) for tag in Tag.objects.all()]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def categories(request: HttpRequest):
    """所有类别"""
    data = [str(category) for category in Category.objects.all()]
    return JsonResponse({"data": data, "code": "200"})
