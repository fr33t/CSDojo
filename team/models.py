from django.db import models
from account.models import User
from django.utils import timezone


# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="团队名称")
    description = models.TextField(verbose_name="描述")
    captain = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="captain_team",
        blank=True,
    )
    users = models.ManyToManyField(User, related_name="member_teams", blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "captain": self.captain.nickname,
        }


class TeamRequest(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="team_requests",
        blank=True,
        null=True,
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="team_requests",
        null=True,
        blank=True,
    )
    submitted_at = models.DateTimeField(default=timezone.now)

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user.nickname,
            "team": self.team.name,
            "submitted_at": self.submitted_at,
        }

    def __str__(self):
        return f"{str(self.team)}-{str(self.user)}"
