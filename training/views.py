from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from challenge.models import Challenge
from .models import Training, TrainingLog
from account.models import User
from CSDojo.settings import CUSTOM_URL_PREFIX
from CSDojo.utils import (
    require_json_content_type,
    validate_request_data_json_decorator,
    jwt_required,
    generate_flag,
    docker_client,
)


@require_GET
@jwt_required
def trainings(request: HttpRequest):
    user = User.objects.get(email=request.jdata["email"])
    ts = user.trainings.filter(status=1)

    data = [t.to_dict() for t in ts]
    return JsonResponse({"data": data, "code": "200"})


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["challenge_id"])
def create(request: HttpRequest):
    data = request.vdata
    challenges = Challenge.objects.filter(id=data["challenge_id"])
    user = User.objects.get(email=request.jdata["email"])
    if len(challenges) == 0:
        return JsonResponse({"message": "题目不存在", "code": "404"})

    challenge_data = challenges[0].from_toml()
    # 检验是否已经存在
    t = user.trainings.filter(challenge=challenges[0], status=1)
    if len(t) != 0:
        return JsonResponse({"message": "环境已存在", "code": "301"})

    training = Training()
    training.challenge = challenges[0]
    training.user = user
    training.created_at = timezone.now()
    training.status = 0
    training.save()

    training.cpu_limit = challenge_data["cpu_limit"]
    training.memory_limit = challenge_data["memory_limit"]
    training.disk_limit = challenge_data["disk_limit"]
    if challenge_data["is_dynamic"]:
        training.flag = generate_flag()
    else:
        training.flag = challenge_data["static_flag"]

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
            environment={"FLAG": training.flag},
            detach=True,  # restart
        )
    except Exception as e:
        print(e)
        return JsonResponse({"message": "是我们的服务器出问题了！", "code": "500"})

    container.reload()
    port_bindings = container.attrs["NetworkSettings"]["Ports"]
    # 提取随机端口
    random_port = port_bindings[f"{challenge_data['port']}/tcp"][0]["HostPort"]
    # flag
    training.status = 1
    training.container_id = container.id
    training.content = f"{CUSTOM_URL_PREFIX}:{random_port}/"
    training.started_at = timezone.now()
    training.status = 1
    training.save()
    return JsonResponse(
        {"message": "创建成功", "training_id": training.id, "code": "200"}
    )


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["training_id"])
def destroy(request: HttpRequest):
    data = request.vdata
    ts = Training.objects.filter(id=data["training_id"])
    if len(ts) == 0:
        return JsonResponse({"message": "环境不存在", "code": "404"})
    try:
        training = ts[0]
        training.status = 2
        training.stopped_at = timezone.now()
        container = docker_client.containers.get(training.container_id)
        container.remove(force=True)
        training.save()
        return JsonResponse({"message": "销毁成功", "code": "200"})
    except Exception:
        return JsonResponse({"message": "容器不存在", "code": "404"})


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["training_id", "flag"])
def submit(request: HttpRequest):
    data = request.vdata
    user = User.objects.get(email=request.jdata["email"])
    ts = user.trainings.filter(id=data["training_id"], status=1)

    if len(ts) == 0:
        return JsonResponse({"message": "环境不存在", "code": "404"})
    try:
        training = ts[0]
        training_log = TrainingLog()
        training_log.submitted_at = timezone.now()
        training_log.submitted_flag = data["flag"]
        training_log.training = training
        training_log.user = user

        if training.flag == training_log.submitted_flag:
            training.stopped_at = timezone.now()
            training.status = 2
            training.pwnd = True
            training.save()

            training_log.is_correct = True
            training_log.save()

            try:
                container = docker_client.containers.get(training.container_id)
                container.remove(force=True)
            except Exception:
                return JsonResponse(
                    {"message": "FLAG正确但容器删除失败", "code": "501"}
                )
            return JsonResponse({"message": "FLAG正确", "code": "200"})
        else:
            training_log.save()
            return JsonResponse({"message": "FLAG错误", "code": "400"})

    except Exception:
        return JsonResponse({"message": "容器不存在", "code": "404"})


# extend time
@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["training_id"])
def extend_time(request: HttpRequest):
    data = request.vdata
    ts = Training.objects.filter(id=data["training_id"])
    if len(ts) == 0:
        return JsonResponse({"message": "环境不存在", "code": "404"})

    training = ts[0]

    if not training.can_extend:
        return JsonResponse(
            {
                "message": f"当时间小于30分钟可延长， 最大可延长{training.max_extend_count}次",
                "code": "400",
            }
        )

    training.extend_count += 1
    training.save()

    return JsonResponse({"message": "延长成功", "code": "200"})
