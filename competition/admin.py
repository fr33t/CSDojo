from django.contrib import admin
from .models import (
    Competition,
    CompetitionTraining,
    CompetitionTrainingLog,
)


@admin.register(Competition)
class CompetitionModelAdmin(admin.ModelAdmin):
    pass


@admin.register(CompetitionTraining)
class CompetitionTrainingModelAdmin(admin.ModelAdmin):
    pass


@admin.register(CompetitionTrainingLog)
class CompetitionTrainingLogModelAdmin(admin.ModelAdmin):
    pass
