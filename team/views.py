from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from account.models import User
from .models import Team, TeamRequest

from CSDojo.utils import (
    require_json_content_type,
    validate_request_data_json_decorator,
    jwt_required,
)


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["name", "description"])
def create(request: HttpRequest):
    user = User.objects.get(email=request.jdata["email"])
    data = request.vdata
    captain_teams = user.captain_team.all()
    member_teams = user.member_teams.all()
    if len(captain_teams) != 0 or len(member_teams) != 0:
        return JsonResponse({"message": "你已经有队伍了", "code": "400"})

    team = Team()
    team.name = data["name"]
    team.description = data["description"]
    team.captain = user
    team.users.add(user)
    try:
        team.save()
    except Exception:
        return JsonResponse({"message": "队伍已经存在了", "code": "4000"})

    return JsonResponse({"message": "队伍创建成功", "code": "200"})


@require_POST
@jwt_required
def quit(request: HttpRequest):
    user = User.objects.get(email=request.jdata["email"])
    captain_teams = user.captain_team.all()
    member_teams = user.member_teams.all()

    if len(captain_teams) != 0:
        team: Team = captain_teams[0]
        team.delete()

    if len(member_teams) != 0:
        team: Team = member_teams[0]
        team.users.remove(user)

    return JsonResponse({"message": "退出团队成功", "code": "200"})


@require_GET
@jwt_required
def teams(request: HttpRequest):
    data = [team.to_dict() for team in Team.objects.all()]
    return JsonResponse({"data": data, "code": "200"})


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["team_id"])
def join(request: HttpRequest):
    data = request.vdata
    ts = Team.objects.filter(id=data["team_id"])
    user = User.objects.get(email=request.jdata["email"])

    captain_teams = user.captain_team.all()
    member_teams = user.member_teams.all()
    if len(captain_teams) != 0 or len(member_teams) != 0:
        return JsonResponse({"message": "你已经有队伍了", "code": "400"})

    if len(ts) == 0:
        return JsonResponse({"message": "队伍不存在", "code": "404"})

    team_request = TeamRequest()
    team_request.user = user
    team_request.team = ts[0]
    team_request.save()
    return JsonResponse({"message": "已提交申请", "code": "200"})


@require_GET
@jwt_required
def requests(request: HttpRequest):
    user = User.objects.get(email=request.jdata["email"])
    captain_teams = user.captain_team.all()

    if len(captain_teams) == 0:
        return JsonResponse({"message": "你不是队长", "code": "400"})
    team_requests = captain_teams[0].team_requests.all()
    data = [tr.to_dict() for tr in team_requests]

    return JsonResponse({"data": data, "code": "200"})


@require_POST
@jwt_required
@validate_request_data_json_decorator(required_fields=["team_id", "agree"])
def handle(request: HttpRequest):
    user = User.objects.get(email=request.jdata["email"])
    trs = TeamRequest.objects.filter(id=requests.vdata["team_id"])
    if len(trs) == 0:
        return JsonResponse({"message": "申请不存在", "code": "404"})
    tr = trs[0]
    if requests.vdata["agree"]:
        member_teams = tr.user.member_teams.all()
        if len(member_teams) != 0:
            return JsonResponse({"message": "他已经有队伍了", "code": "400"})
        captain_teams = user.captain_team.all()
        if len(captain_teams) == 0:
            return JsonResponse({"message": "你不是队长", "code": "400"})
        t: Team = captain_teams[0]
        t.users.add(tr.user)

    tr.delete()

    return JsonResponse({"message": "添加成功", "code": "200"})
