# ruff: noqa: F401
# django
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

# project
from CSDojo.utils import (
    jwt_required,
)

# apps
from account.models import User
from challenge.models import Challenge, Category, Tag

# user
