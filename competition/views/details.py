# ruff: noqa: F401, F403, F405
from . import *


@require_GET
@jwt_required
def competitions(request: HttpRequest):
    """所有比赛无关状态， 前端过滤"""
    data = [competition.to_dict() for competition in Competition.objects.all()]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def challenges(request: HttpRequest, competition_id):
    """某场正在进行的比赛的全部题目"""
    competitions = Competition.objects.filter(id=competition_id, status=1)
    if len(competitions) == 0:
        return JsonResponse({"message": "比赛不存在", "code": "400"})

    competition = competitions[0]
    data = [challenge.to_dict() for challenge in competition.challenges.all()]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def trainings(request: HttpRequest, competition_id):
    """正在进行的比赛中所有开启的环境"""
    competitions = Competition.objects.filter(id=competition_id, status=1)
    if len(competitions) == 0:
        return JsonResponse({"message": "比赛不存在", "code": "400"})
    competition = competitions[0]

    cts = CompetitionTraining.objects.filter(competition=competition, status=1)

    data = [ct.to_dict() for ct in cts]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def joined(request: HttpRequest):
    """用户参加了哪些比赛? 除了结束的"""
    # user and team
    user = User.objects.get(email=request.jdata["email"])

    member_teams = user.member_teams.all()
    team_competitions = set()
    if len(member_teams) != 0:
        mt = member_teams[0]
        team_competitions.add(mt.competitions.exclude(status=2))

    individual_competitions = user.competitions.exclude(status=2)

    individual_competitions_data = [
        individual_competition.to_dict()
        for individual_competition in individual_competitions
    ]
    team_competitions_data = []
    for team_competition in team_competitions:
        for i in team_competition:
            team_competitions_data.append(i.to_dict())

    return JsonResponse(
        {
            "data": {
                "individual_competitions": individual_competitions_data,
                "team_competitions": team_competitions_data,
            },
            "code": "200",
        }
    )
