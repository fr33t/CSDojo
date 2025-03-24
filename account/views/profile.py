# ruff: noqa: F403, F401, F405
from . import *


@require_GET
@jwt_required
def profile(request: HttpRequest):
    """个人资料信息"""
    user = User.objects.get(email=request.jdata["email"])
    # 反向查询
    captain_teams = user.captain_team.all()
    captain_team = {}
    if len(captain_teams) != 0:
        captain_team = {"id": captain_teams[0].id, "name": captain_teams[0].name}
    member_teams = user.member_teams.all()
    member_team = {}
    if len(member_teams) != 0:
        member_team = {"id": member_teams[0].id, "name": member_teams[0].name}
    pwnd_trainings = user.trainings.filter(pwnd=True)

    unique_challenge_trainings = []
    challenge_ids = set()  # 用于记录已经处理过的 challenge id
    for training in pwnd_trainings:
        if training.challenge.id not in challenge_ids:
            unique_challenge_trainings.append(training)
            challenge_ids.add(training.challenge.id)
    challenge_ids = list(challenge_ids)
    data = {
        "nickname": user.nickname,
        "email": user.email,
        "captain_team": captain_team,
        "member_team": member_team,
        "pwnd_challenges": challenge_ids,
        "pwnd_challenges_count": len(challenge_ids),
    }

    return JsonResponse({"data": data, "code": "200"})
