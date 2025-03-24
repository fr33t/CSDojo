# ruff: noqa: F401, F403, F405
from . import *


@require_GET
@jwt_required
def trainings(request: HttpRequest):
    """正在运行中的环境"""
    user = User.objects.get(email=request.jdata["email"])
    ts = user.trainings.filter(status=1)

    data = [t.to_dict() for t in ts]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def detail(request: HttpRequest, challenge_id):
    """对应题目的环境信息"""
    user = User.objects.get(email=request.jdata["email"])
    challenges = Challenge.objects.filter(id=challenge_id)
    if len(challenges) == 0:
        return JsonResponse({"message": "题目不存在", "code": "404"})
    challenge = challenges[0]

    trainings = challenge.trainings.filter(user=user, status=1)
    if len(trainings) == 0:
        return JsonResponse({"message": "环境未开启", "code": "400"})

    data = trainings[0].to_dict()

    return JsonResponse({"data": data, "code": "200"})
