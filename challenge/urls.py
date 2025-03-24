from django.urls import path
from challenge.views import classify, details

urlpatterns = [
    path("top10", details.top10, name="解题前十"),
    path("challenges", details.challenges, name="所有题目"),
    path("detail/<challenge_id>", details.detail, name="单个题目信息"),
    #
    path("tags", classify.tags, name="所有标签"),
    path("categories", classify.categories, name="所有类别"),
]
