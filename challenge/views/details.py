# ruff: noqa: F403, F401, F405
from . import *


@require_GET
@jwt_required
def challenges(request: HttpRequest):
    """所有题目"""
    user = User.objects.get(email=request.jdata["email"])
    data = []
    for challenge in Challenge.objects.filter(visibility=True):
        tdata = challenge.to_dict()
        has_pwnd = False
        trainings = challenge.trainings.filter(user=user, pwnd=True)
        if len(trainings) != 0:
            has_pwnd = True
        tdata["has_pwnd"] = has_pwnd
        data.append(tdata)
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def detail(request: HttpRequest, challenge_id):
    """某个题目的信息"""
    challenges = Challenge.objects.filter(id=challenge_id)
    if len(challenges) == 0:
        return JsonResponse({"message": "题目不存在", "code": "404"})
    challenge = challenges[0]
    data = challenge.to_dict()
    # 是否已经解出了
    has_pwnd = False
    user = User.objects.get(email=request.jdata["email"])
    trainings = challenge.trainings.filter(user=user, pwnd=True)
    if len(trainings) != 0:
        has_pwnd = True

    data["has_pwnd"] = has_pwnd
    return JsonResponse({"data": data, "code": "200"})


@require_GET
def top10(request: HttpRequest):
    """解题数前10名"""
    users = User.objects.all()
    data = []
    for user in users:
        pwnd_trainings = user.trainings.filter(pwnd=True)
        unique_challenge_trainings = []
        challenge_ids = set()  # 用于记录已经处理过的 challenge id
        for training in pwnd_trainings:
            if training.challenge.id not in challenge_ids:
                unique_challenge_trainings.append(training)
                challenge_ids.add(training.challenge.id)
        challenge_ids = list(challenge_ids)
        t_data = {
            "nickname": user.nickname,
            "email": user.email,
            "pwnd_challenges": challenge_ids,
            "pwnd_challenges_count": len(challenge_ids),
        }
        data.append(t_data)

    sorted_data = sorted(data, key=lambda x: x["pwnd_challenges_count"], reverse=True)

    # 取前 10 条记录
    top10_data = sorted_data[:10]
    return JsonResponse({"data": top10_data, "code": "200"})
