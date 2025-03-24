# ruff: noqa: F401
# django
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone

# project
from CSDojo.settings import CUSTOM_IP_PREFIX

# Create your views here.
from CSDojo.utils import (
    require_json_content_type,
    jwt_required,
    validate_request_data_json_decorator,
    generate_flag,
    docker_client,
)

# apps
from competition.models import (
    Competition,
    CompetitionTraining,
    CompetitionTrainingLog,
    CompetitionAnnouncement,
    CompetitionChallengePwnd,
    get_score,
)
from account.models import User
from challenge.models import Challenge
