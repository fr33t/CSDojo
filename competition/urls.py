from django.urls import path
from competition.views import details, manage

urlpatterns = [
    path("submit", manage.submit, name="提交题目的flag"),
    path("create_training", manage.create_training, name="创建题目环境"),
    path("destroy_training", manage.destroy_training, name="销毁题目环境"),
    #
    path("joined", details.joined, name="用户参加了那些比赛"),
    path("competitions", details.competitions, name="所有比赛"),
    path("challenges/<competition_id>", details.challenges, name="比赛的所有题目"),
    path("trainings/<competition_id>", details.trainings, name="比赛中的运行中的环境"),
]
