from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


from CSDojo.utils import (
    jwt_required,
)

from .models import Challenge, Tag, Category


@require_GET
@jwt_required
def challenges(request: HttpRequest):
    data = [c.to_dict() for c in Challenge.objects.filter(visibility=True)]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def tags(request: HttpRequest):
    data = [str(tag) for tag in Tag.objects.all()]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def categories(request: HttpRequest):
    data = [str(category) for category in Category.objects.all()]
    return JsonResponse({"data": data, "code": "200"})
