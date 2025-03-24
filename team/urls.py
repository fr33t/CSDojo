from django.urls import path
from team.views import manage, details

urlpatterns = [
    path("teams", details.teams, name="都有哪些队伍"),
    path("requests", details.requests, name="入队请求"),
    #
    path("quit", manage.quit, name="退出或解散队伍"),
    path("join", manage.join, name="申请加入队伍"),
    path("create", manage.create, name="创建队伍"),
    path("handle", manage.handle, name="处理入队请求"),
]
