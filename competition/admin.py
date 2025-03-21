from django.contrib import admin
from .models import (
    Competition,
    CompetitionTraining,
    CompetitionTrainingLog,
    CompetitionChallengePwnd,
    CompetitionAnnouncement,
)


@admin.register(Competition)
class CompetitionModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "is_team",
        "status",
        "start_time",
        "end_time",
    )
    list_display_links = ("id", "name")
    search_fields = ("name",)
    list_filter = ("category", "is_team", "status")


@admin.register(CompetitionTraining)
class CompetitionTrainingModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "container_id",
        "status",
        "pwnd",
        "created_at",
        "stopped_at",
    )

    list_display_links = (
        "id",
        "name",
        "container_id",
    )

    search_fields = (
        "name",
        "container_id",
    )

    list_filter = (
        "status",
        "pwnd",
    )

    def name(self, obj):
        return str(obj)


@admin.register(CompetitionTrainingLog)
class CompetitionTrainingLogModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "is_correct",
        "score",
        "submitted_flag",
        "submitted_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "submitted_flag",
    )

    list_filter = ("is_correct",)

    def name(self, obj):
        return str(obj)


@admin.register(CompetitionChallengePwnd)
class CompetitionChallengePwndModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "team",
        "order",
        "created_at",
    )

    list_display_links = ("id", "name")
    search_fields = ("name", "user", "team")

    def name(self, obj):
        return str(obj)


@admin.register(CompetitionAnnouncement)
class CompetitionAnnouncementModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "team",
        "user_score",
        "team_score",
        "updated_at",
    )
    search_fields = (
        "name",
        "user",
        "team",
    )
    list_display_links = ("id", "name")

    def name(self, obj):
        return str(obj)
