# ruff: noqa: F401
# django
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone

# project
from CSDojo.settings import CUSTOM_IP_PREFIX
from CSDojo.utils import (
    require_json_content_type,
    validate_request_data_json_decorator,
    jwt_required,
    generate_flag,
    docker_client,
)

# apps
from challenge.models import Challenge
from training.models import Training, TrainingLog
from account.models import User

# user
