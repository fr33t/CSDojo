from django.db import models
from account.models import User
from challenge.models import Challenge
from training.models import Training
from team.models import Team


class Competition(models.Model):
    STATUS = [
        (0, "未开始"),
        (1, "进行中"),
        (2, "已结束"),
        (3, "已暂停"),
    ]

    CATEGORIES = [
        (0, "CTF"),
        (1, "AWD"),
        (2, "ISW"),
    ]

    name = models.CharField(max_length=255, verbose_name="比赛名称")
    status = models.IntegerField(default=0, choices=STATUS, verbose_name="比赛状态")
    category = models.IntegerField(
        default=0, choices=CATEGORIES, verbose_name="比赛类型"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(verbose_name="比赛介绍")
    rules = models.TextField(verbose_name="规则")
    challenges = models.ManyToManyField(
        Challenge, related_name="competitions", verbose_name="题目"
    )
    is_team = models.BooleanField(default=False, verbose_name="是否是团队赛")
    users = models.ManyToManyField(
        User,
        related_name="competitions",
        verbose_name="个人赛选择",
        blank=True,
    )
    teams = models.ManyToManyField(
        Team,
        related_name="competitions",
        verbose_name="团队赛选择",
        blank=True,
    )

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_team": self.is_team,
            "status": self.get_status_display(),
            "category": self.get_category_display(),
        }


class CompetitionTraining(Training):
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="competition_trainings",
        blank=True,
        null=True,
    )


class CompetitionTrainingLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    training = models.ForeignKey(CompetitionTraining, on_delete=models.CASCADE)
    submitted_flag = models.CharField(max_length=255, verbose_name="用户提交的FLAG")
    is_correct = models.BooleanField(default=False, verbose_name="提交的是否正确")
    submitted_at = models.DateTimeField(verbose_name="提交时间")
    score = models.FloatField(verbose_name="该题得分", blank=True, null=True)


# Competition 可无视visibility

# CompetitionLog

# CompetitionAnnouncement
# 得分 排行榜 数据图
