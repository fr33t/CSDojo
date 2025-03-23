"""
WSGI config for CSDojo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from django.utils import timezone
from training.models import Training
from competition.models import Competition
import pytz
from CSDojo.utils import docker_client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CSDojo.settings")

application = get_wsgi_application()


scheduler_started = False


def clean_outdate_trainings():
    print(f"Training: 开始清理过期环境: {datetime.now()}")
    trainings = Training.objects.filter(status=1)
    for training in trainings:
        if training.remaining_time <= 0:
            training.status = 2
            training.stopped_at = timezone.now()
            if training.challenge.is_dockerd:
                container = docker_client.containers.get(training.container_id)
                container.remove(force=True)
            training.save()
            print(f"Training: 销毁 {str(training)}")


def clean_outdate_competition():
    print(f"Competition: 开始清理过期环境: {datetime.now()}")
    competitions = Competition.objects.filter(status=1)

    for competition in competitions:
        if competition.remaining_time <= 0:
            competition.status = 2
            competition.save()

        competition_trainings = competition.competition_trainings.filter(status=1)
        for competition_training in competition_trainings:
            if competition_training.remaining_time <= 0 or competition.status == 2:
                # 比赛结束 销毁所有， 没结束 到期的销毁

                competition_training.status = 2
                competition_training.stopped_at = timezone.now()
                if competition_training.challenge.is_dockerd:
                    container = docker_client.containers.get(
                        competition_training.container_id
                    )
                    container.remove(force=True)
                competition_training.save()
                print(f"Competition Training: 销毁 {str(competition_training)}")


def start_competition(competition: Competition):
    try:
        competition.status = 1
        competition.save()
        print(f"Competition Start: {competition.name}已开始 {timezone.now()}")
    except Exception as e:
        print(f"Competition Start:{e}")


def end_competition(competition: Competition):
    try:
        competition.status = 2
        competition.save()
        print(f"Competition Start: {competition.name}已结束 {timezone.now()}")
        competition_trainings = competition.competition_trainings.filter(status=1)
        for competition_training in competition_trainings:
            competition_training.status = 2
            competition_training.stopped_at = timezone.now()
            if competition_training.challenge.is_dockerd:
                container = docker_client.containers.get(
                    competition_training.container_id
                )
                container.remove(force=True)
            competition_training.save()
            print(f"Competition End Training: 销毁 {str(competition_training)}")
    except Exception as e:
        print(f"Competition Start:{e}")


scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Shanghai"))


def check_competitions():
    global scheduler
    competitions = Competition.objects.filter(status=0)
    print("Competitions Check: 检查所有比赛的定时器")
    for competition in competitions:
        scheduler.add_job(
            start_competition,
            "date",
            run_date=competition.start_time,
            args=[competition],
            id=f"competition_start_{competition.id}",
            replace_existing=True,
        )
        scheduler.add_job(
            end_competition,
            "date",
            run_date=competition.end_time,
            args=[competition],
            id=f"competition_end_{competition.id}",
            replace_existing=True,
        )


check_competitions()
scheduler.add_job(check_competitions, "interval", minutes=1)
scheduler.add_job(clean_outdate_trainings, "interval", minutes=1)
scheduler.add_job(clean_outdate_competition, "interval", minutes=3)

scheduler.start()
