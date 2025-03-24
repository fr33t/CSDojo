# ruff: noqa: F401
# django
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET

# project
from CSDojo.utils import (
    require_json_content_type,
    validate_request_data_json_decorator,
    jwt_required,
)

# apps
from account.models import User
from team.models import Team, TeamRequest

# user
