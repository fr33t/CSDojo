from django.urls import path
from . import views

urlpatterns = [
    path("challenges", views.challenges),
    path("tags", views.tags),
    path("categories", views.categories),
]
