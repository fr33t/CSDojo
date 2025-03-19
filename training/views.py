from django.shortcuts import render
from django.http import HttpRequest
from django.views.decorators.http import require_POST, require_GET


from CSDojo.utils import (
    require_json_content_type,
    validate_request_data_json_decorator,
    jwt_required,
)


@require_GET
@jwt_required
def trainings(request: HttpRequest):
    pass
