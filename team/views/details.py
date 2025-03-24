# ruff: noqa: F401, F403, F405
from . import *


@require_GET
@jwt_required
def teams(request: HttpRequest):
    """都有那些队伍"""
    data = [team.to_dict() for team in Team.objects.all()]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def requests(request: HttpRequest):
    """队长收到的入队请求"""
    user = User.objects.get(email=request.jdata["email"])
    captain_teams = user.captain_team.all()

    if len(captain_teams) == 0:
        return JsonResponse({"message": "你不是队长", "code": "400"})
    team_requests = captain_teams[0].team_requests.all()
    data = [tr.to_dict() for tr in team_requests]

    return JsonResponse({"data": data, "code": "200"})
