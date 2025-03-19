from django.db import models
from challenge.models import Challenge
from account.models import User
from django.utils import timezone

# flag 题目ID 解题状态
# history 创建时间 销毁时间 谁开启的 Training 题目ID 是否解出 谁交的flag


# Create your models here.
class Training(models.Model):
    """本身就是 History， 获取过滤STATUS=2 和 user_id="""

    STATUS = [
        (0, "启动中"),
        (1, "运行中"),
        (2, "已停止"),
        (3, "错误"),
    ]

    challenge = models.ForeignKey(
        Challenge, on_delete=models.CASCADE, verbose_name="题目"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="谁开启的题目"
    )

    status = models.IntegerField(choices=STATUS, default=0, verbose_name="题目状态")
    content = models.CharField(
        max_length=500, verbose_name="题目内容", null=True, blank=True
    )

    flag = models.CharField(
        max_length=255, verbose_name="FLAG值", null=True, blank=True
    )
    pwnd = models.BooleanField(default=False, verbose_name="是否被攻破")

    # docker about
    container_id = models.CharField(
        max_length=255, verbose_name="DOCKER容器id", null=True, blank=True
    )
    cpu_limit = models.PositiveIntegerField(
        default=1, verbose_name="CPU核数", null=True, blank=True
    )
    memory_limit = models.PositiveIntegerField(
        default=64, verbose_name="分配内存", null=True, blank=True
    )
    disk_limit = models.PositiveIntegerField(default=256, verbose_name="磁盘空间")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="启动时间")

    default_duration = models.PositiveIntegerField(default=3600)
    extend_duration = models.PositiveIntegerField(default=1800)
    extend_count = models.PositiveIntegerField(default=0)
    max_extend_count = models.PositiveIntegerField(default=3)

    stopped_at = models.DateTimeField(null=True, blank=True, verbose_name="停止时间")
    # 启动时 启动一个 timer 时间到期删除docker和 将Training STATUS改为stop

    # 计算剩余时间
    @property
    def remaining_time(self):
        total_duration = self.default_duration + (
            self.extend_count * self.extend_duration
        )
        elapsed_time = (timezone.now() - self.started_at).total_seconds()
        return max(total_duration - elapsed_time, 0)

    @property
    def can_extend(self):
        return self.remaining_time < 1800 and self.extend_count < self.max_extend_count

    def __str__(self):
        return f"{self.challenge.title}-{self.user.nickname}"


class TrainingLog(models.Model):
    """User Attempt"""

    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_flag = models.CharField(max_length=255, verbose_name="用户提交的FLAG")
    is_correct = models.BooleanField(default=False, verbose_name="提交的是否正确")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")

    def __str__(self):
        return f"{self.training.challenge.title}-{self.user.nickname}"
