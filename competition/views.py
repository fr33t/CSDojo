from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from .models import (
    Competition,
    CompetitionTraining,
    CompetitionTrainingLog,
    CompetitionAnnouncement,
    CompetitionChallengePwnd,
    get_score,
)
from account.models import User
from challenge.models import Challenge

from CSDojo.settings import CUSTOM_IP_PREFIX

# Create your views here.
from CSDojo.utils import (
    require_json_content_type,
    jwt_required,
    validate_request_data_json_decorator,
    generate_flag,
    docker_client,
)


# all competitions
@require_GET
@jwt_required
def competitions(request: HttpRequest):
    data = [competition.to_dict() for competition in Competition.objects.all()]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def joined(request: HttpRequest):
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


@require_GET
@jwt_required
def challenges(request: HttpRequest, competition_id):
    competitions = Competition.objects.filter(id=competition_id, status=1)
    if len(competitions) == 0:
        return JsonResponse({"message": "比赛不存在", "code": "400"})

    competition = competitions[0]
    data = [challenge.to_dict() for challenge in competition.challenges.all()]
    return JsonResponse({"data": data, "code": "200"})


@require_GET
@jwt_required
def trainings(request: HttpRequest, competition_id):
    competitions = Competition.objects.filter(id=competition_id, status=1)
    if len(competitions) == 0:
        return JsonResponse({"message": "比赛不存在", "code": "400"})
    competition = competitions[0]

    cts = CompetitionTraining.objects.filter(competition=competition, status=1)

    data = [ct.to_dict() for ct in cts]
    return JsonResponse({"data": data, "code": "200"})


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(
    required_fields=["competition_id", "challenge_id"]
)
def create_training(request: HttpRequest):
    data = request.vdata

    challenges = Challenge.objects.filter(id=data["challenge_id"])
    if len(challenges) == 0:
        return JsonResponse({"message": "题目不存在", "code": "404"})

    competitions = Competition.objects.filter(id=data["competition_id"], status=1)
    if len(competitions) == 0:
        return JsonResponse({"message": "比赛不存在", "code": "404"})

    challenge = challenges[0]
    competition = competitions[0]
    user = User.objects.get(email=request.jdata["email"])

    ct = CompetitionTraining.objects.filter(
        challenge=challenge, competition=competition, status=1
    )
    if len(ct) != 0:
        return JsonResponse({"message": "环境已存在", "code": "301"})

    ct = CompetitionTraining()
    # team
    if competition.is_team:
        teams = competition.teams.filter(users=user)
        if len(teams) == 0:
            return JsonResponse({"message": "你的队伍没有参加这个比赛", "code": "200"})
        ct.team = teams[0]

    ct.user = user
    ct.challenge = challenge
    ct.competition = competition
    ct.created_at = timezone.now()
    ct.status = 0
    ct.save()

    challenge_data = challenge.from_toml()
    ct.cpu_limit = challenge_data["cpu_limit"]
    ct.memory_limit = challenge_data["memory_limit"]
    ct.disk_limit = challenge_data["disk_limit"]
    if challenge_data["is_dynamic"]:
        ct.flag = generate_flag()
    else:
        ct.flag = challenge_data["static_flag"]
    random_port = None
    if challenge.is_dockerd:
        try:
            container = docker_client.containers.run(
                image=challenge_data["docker_image"],
                ports={
                    challenge_data["port"]: None,
                },
                cpu_quota=int(challenge_data["cpu_limit"] * 1e5),
                mem_limit=f"{challenge_data['memory_limit']}m",
                # storage_opt={"size": f"{challenge_data['disk_limit']}m"}, XFS overlay2
                privileged=challenge_data["privileged"],
                environment={"FLAG": ct.flag},
                detach=True,  # restart
            )
            container.reload()
            port_bindings = container.attrs["NetworkSettings"]["Ports"]
            # 提取随机端口
            random_port = port_bindings[f"{challenge_data['port']}/tcp"][0]["HostPort"]
            # flag
            ct.container_id = container.id
        except Exception as e:
            print(e)
            return JsonResponse({"message": "是我们的服务器出问题了！", "code": "500"})

    if challenge["is_nc"]:
        ct.content = f"nc {CUSTOM_IP_PREFIX} {random_port}"
    elif random_port:
        # // challenge.category
        ct.content = f'<a class="underline-offset-4 hover:underline" href="http://{CUSTOM_IP_PREFIX}:{random_port}" target="_blank">http://{CUSTOM_IP_PREFIX}:{random_port}</a>'
    ct.started_at = timezone.now()
    ct.status = 1
    ct.save()
    return JsonResponse(
        {"message": "创建成功", "competition_training_id": ct.id, "code": "200"}
    )


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["competition_training_id"])
def destroy_training(request: HttpRequest):
    data = request.vdata
    ct = CompetitionTraining.objects.filter(
        id=data["competition_training_id"], status=1
    )
    if len(ct) == 0:
        return JsonResponse({"message": "环境不存在", "code": "404"})

    try:
        competition_training = ct[0]
        competition_training.status = 2
        competition_training.stopped_at = timezone.now()
        if competition_training.challenge.is_dockerd:
            container = docker_client.containers.get(competition_training.container_id)
            container.remove(force=True)
        competition_training.save()
        return JsonResponse({"message": "销毁成功", "code": "200"})
    except Exception:
        return JsonResponse({"message": "容器不存在", "code": "404"})


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(
    required_fields=["competition_training_id", "flag"]
)  # wp
def submit(request: HttpRequest):
    data = request.vdata
    user = User.objects.get(email=request.jdata["email"])
    ct = CompetitionTraining.objects.filter(
        id=data["competition_training_id"], status=1
    )

    if len(ct) == 0:
        return JsonResponse({"message": "环境不存在", "code": "404"})

    try:
        competition_training = ct[0]
        competition_training_log = CompetitionTrainingLog()
        competition_training_log.submitted_at = timezone.now()
        competition_training_log.submitted_flag = data["flag"]
        competition_training_log.training = competition_training
        competition_training_log.user = user
        competition_training_log.competition = competition_training.competition

        if competition_training.flag == competition_training_log.submitted_flag:
            competition_training.stopped_at = timezone.now()
            competition_training.status = 2
            competition_training.pwnd = True
            competition_training.save()

            competition_training_log.is_correct = True
            competition_training_log.save()

            competition_challenge_pwnd = CompetitionChallengePwnd()
            competition_challenge_pwnd.competition = (
                competition_training_log.competition
            )
            competition_challenge_pwnd.challenge = competition_training.challenge
            competition_challenge_pwnd.user = user
            competition_challenge_pwnd.save()  # 现刷新order

            # 取出已有的计分板
            competition_announcements = CompetitionAnnouncement.objects.filter(
                competition=competition_training_log.competition, user=user
            )
            if len(competition_announcements) == 0:
                competition_announcement = CompetitionAnnouncement()
            else:
                competition_announcement = competition_announcements[0]
            # 设置分数
            competition_announcement.competition = competition_training_log.competition
            competition_announcement.updated_at = timezone.now()
            score = get_score(competition_challenge_pwnd.order)
            competition_announcement.user_score += score
            competition_training_log.score = score
            competition_announcement.save()
            competition_announcement.pwnd_challenges.add(
                competition_training_log.training.challenge
            )

            if competition_training_log.competition.is_team:
                teams = competition_training_log.competition.teams.filter(users=user)
                if len(teams) == 0:
                    return JsonResponse(
                        {"message": "你的队伍没有参加这个比赛", "code": "200"}
                    )
                competition_challenge_pwnd.team = teams[0]
                competition_announcement.team = teams[0]
                competition_announcement.team_score += score

            competition_challenge_pwnd.save()
            competition_announcement.save()
            if competition_training.challenge.is_dockerd:
                try:
                    container = docker_client.containers.get(
                        competition_training.container_id
                    )
                    container.remove(force=True)
                except Exception:
                    return JsonResponse(
                        {"message": "FLAG正确但容器删除失败", "code": "501"}
                    )

            return JsonResponse({"message": "FLAG正确", "code": "200"})
        else:
            competition_training_log.save()
            return JsonResponse({"message": "FLAG错误", "code": "400"})

    except Exception as e:
        raise e
        return JsonResponse({"message": "容器不存在", "code": "404"})
