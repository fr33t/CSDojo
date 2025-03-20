from django.contrib import admin
from .models import Training, TrainingLog


@admin.register(Training)
class TrainingModelAdmin(admin.ModelAdmin):
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


@admin.register(TrainingLog)
class TrainingLogModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "is_correct",
        "submitted_flag",
        "submitted_at",
    )

    list_display_links = (
        "id",
        "name",
        "submitted_flag",
    )

    search_fields = (
        "name",
        "submitted_flag",
    )

    list_filter = ("is_correct",)

    def name(self, obj):
        return str(obj)
