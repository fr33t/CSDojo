from django.urls import path
from . import views

urlpatterns = [
    path("trainings", views.trainings),
    path("create", views.create),
    path("destroy", views.destroy),
    path("submit", views.submit),
    path("extend_time", views.extend_time),
    path("detail/<challenge_id>", views.detail),
]
