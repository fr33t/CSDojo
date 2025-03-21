from django.db import models
from account.models import User
from challenge.models import Challenge
from training.models import Training
from team.models import Team
from django.utils import timezone


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

    @property
    def remaining_time(self):
        elapsed_time = (self.end_time - timezone.now()).total_seconds()
        return max(elapsed_time, 0)

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
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)

    def to_dict(self):
        data = super().to_dict()
        data["competition"] = self.competition.id
        if self.competition.is_team:
            data["team"] = self.team.name
        return data

    def __str__(self):
        return f"{self.competition.name}-{self.challenge}"


# 分数衰减 500×(1÷(0.01×(10+99)))
class CompetitionTrainingLog(models.Model):
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    training = models.ForeignKey(CompetitionTraining, on_delete=models.CASCADE)
    submitted_flag = models.CharField(max_length=255, verbose_name="用户提交的FLAG")
    is_correct = models.BooleanField(default=False, verbose_name="提交的是否正确")
    submitted_at = models.DateTimeField(verbose_name="提交时间")
    score = models.FloatField(default=0, verbose_name="该题得分", blank=True, null=True)

    def __str__(self):
        return f"{self.training}"


# 先后解题顺序
class CompetitionChallengePwnd(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.SET_NULL, null=True)
    order = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.competition.name}-{self.challenge.title}"

    def save(self, *args, **kwargs):
        if not self.pk:
            # 获取当前 competition 和 challenge 的最大 order 值
            max_order = CompetitionChallengePwnd.objects.filter(
                competition=self.competition, challenge=self.challenge
            ).aggregate(models.Max("order"))["order__max"]
            # 如果 max_order 为 None，说明是第一个记录，从 1 开始
            self.order = 1 if max_order is None else max_order + 1
        super().save(*args, **kwargs)


# 已经解过的题不可开启 就无法重新提交flag


# 得分 排行榜 数据图
class CompetitionAnnouncement(models.Model):
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE
    )  # 存放了 团队赛还是 个人赛 查询分数
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    pwnd_challenges = models.ManyToManyField(Challenge)
    team_score = models.FloatField(default=0.0)  # 团队总分
    user_score = models.FloatField(default=0.0)  # 个人总分
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField()

    def __str__(self):
        return f"{self.competition.name}"


def get_score(order):
    return 500 * (1 / (0.01 * (order + 99)))
