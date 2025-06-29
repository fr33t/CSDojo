# ruff: noqa: F401, F403, F405
from . import *


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["name", "description"])
def create(request: HttpRequest):
    """创建队伍"""
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
    """退出队伍， 队长退出队伍解散"""
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


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["team_id"])
def join(request: HttpRequest):
    """申请加入队伍"""
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


@require_POST
@jwt_required
@validate_request_data_json_decorator(required_fields=["team_id", "agree"])
def handle(request: HttpRequest):
    """队长处理入队请求"""
    user = User.objects.get(email=request.jdata["email"])
    trs = TeamRequest.objects.filter(id=request.vdata["team_id"])
    if len(trs) == 0:
        return JsonResponse({"message": "申请不存在", "code": "404"})
    tr = trs[0]
    if request.vdata["agree"]:
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
