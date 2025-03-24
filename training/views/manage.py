# ruff: noqa: F401, F403, F405
from . import *


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["challenge_id"])
def create(request: HttpRequest):
    """创建题目环境"""
    data = request.vdata
    challenges = Challenge.objects.filter(id=data["challenge_id"])
    user = User.objects.get(email=request.jdata["email"])
    if len(challenges) == 0:
        return JsonResponse({"message": "题目不存在", "code": "404"})

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

    challenge_data = challenges[0].from_toml()
    training.cpu_limit = challenge_data["cpu_limit"]
    training.memory_limit = challenge_data["memory_limit"]
    training.disk_limit = challenge_data["disk_limit"]
    if challenge_data["is_dynamic"]:
        training.flag = generate_flag()
    else:
        training.flag = challenge_data["static_flag"]
    random_port = None
    if challenges[0].is_dockerd:
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
        training.container_id = container.id

    if challenge_data["is_nc"]:
        training.content = f"nc {CUSTOM_IP_PREFIX} {random_port} "
    elif random_port:
        # // challenge.category
        training.content = f'<a class="underline-offset-4 hover:underline" href="http://{CUSTOM_IP_PREFIX}:{random_port}" target="_blank"">http://{CUSTOM_IP_PREFIX}:{random_port}</a>'
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
    """销毁题目环境"""
    data = request.vdata
    ts = Training.objects.filter(id=data["training_id"])
    if len(ts) == 0:
        return JsonResponse({"message": "环境不存在", "code": "404"})
    try:
        training = ts[0]
        training.status = 2
        training.stopped_at = timezone.now()
        if training.challenge.is_dockerd:
            container = docker_client.containers.get(training.container_id)
            container.remove(force=True)
        training.save()
        return JsonResponse({"message": "销毁成功", "code": "200"})
    except Exception:
        return JsonResponse({"message": "容器不存在", "code": "404"})


# extend time
@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["training_id"])
def extend_time(request: HttpRequest):
    """增加环境时间， flag过期"""
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


@require_POST
@jwt_required
@require_json_content_type
@validate_request_data_json_decorator(required_fields=["training_id", "flag"])
def submit(request: HttpRequest):
    """提交flag"""
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
            if training.challenge.is_dockerd:
                try:
                    container = docker_client.containers.get(training.container_id)
                    container.remove(force=True)
                except Exception:
                    return JsonResponse(
                        {"message": "FLAG正确但容器删除失败", "code": "200"}
                    )

            return JsonResponse({"message": "FLAG正确", "code": "200"})
        else:
            training_log.save()
            return JsonResponse({"message": "FLAG错误", "code": "400"})

    except Exception:
        return JsonResponse({"message": "容器不存在", "code": "404"})
