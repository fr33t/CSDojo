from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .models import Competition

# Create your views here.
from CSDojo.utils import require_json_content_type, jwt_required


# all competitions
@require_GET
@jwt_required
def competitions(request: HttpRequest):
    data = [competition.to_dict() for competition in Competition.objects.all()]
    return JsonResponse({"data": data, "code": "200"})
