from django.urls import path
from training.views import manage, details

urlpatterns = [
    path("create", manage.create, name="创建题目环境"),
    path("submit", manage.submit, name="提交flag"),
    path("destroy", manage.destroy, name="销毁环境"),
    path("extend_time", manage.extend_time, name="延长环境时间"),
    #
    path("trainings", details.trainings, name="正在运行的环境"),
    path("detail/<challenge_id>", details.detail, name="对应题目的环境信息"),
]
