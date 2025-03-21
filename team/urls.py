from django.urls import path
from . import views

urlpatterns = [
    path("create", views.create),
    path("quit", views.quit),
    path("teams", views.teams),
    path("join", views.join),
    path("requests", views.requests),
    path("handle", views.handle),
]
