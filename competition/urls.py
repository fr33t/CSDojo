from django.urls import path
from . import views

urlpatterns = [
    path("competitions", views.competitions),
    path("joined", views.joined),
    path("challenges/<competition_id>", views.challenges),
    path("trainings/<competition_id>", views.trainings),
    path("create_training", views.create_training),
    path("destroy_training", views.destroy_training),
    path("submit", views.submit),
]
