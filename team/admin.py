from django.contrib import admin
from .models import Team, TeamRequest


# Register your models here.
# Register your models here.
@admin.register(Team)
class TeamModelAdmin(admin.ModelAdmin):
    pass


@admin.register(TeamRequest)
class TeamRequestModelAdmin(admin.ModelAdmin):
    pass
