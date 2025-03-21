from django.contrib import admin
from .models import Team, TeamRequest


# Register your models here.
# Register your models here.
@admin.register(Team)
class TeamModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "captain", "created_at")
    list_display_links = ("id", "name")
    search_fields = ("name", "captain")


@admin.register(TeamRequest)
class TeamRequestModelAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "user", "submitted_at")
    list_display_links = ("id", "team")
    search_fields = ("team", "user")
