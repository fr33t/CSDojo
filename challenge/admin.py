from django.contrib import admin
from django.contrib import messages
from .models import Category, Tag, Challenge

admin.site.register(Category)
admin.site.register(Tag)


# Register your models here.
@admin.register(Challenge)
class ChallengeModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "category",
        "difficulty",
        "visibility",
        "image_existed",
    )
    list_display_links = (
        "id",
        "title",
    )

    search_fields = (
        "title",
        "author",
    )

    list_filter = (
        "category",
        "difficulty",
        "visibility",
        "image_existed",
        "tags",
    )

    def save_related(self, request, form, formsets, change):
        challenge_instance: Challenge = form.instance
        try:
            challenge_instance.build_image()
            challenge_instance.image_existed = True
            challenge_instance.save()
        except Exception as e:
            messages.error(request, f"镜像构建或拉取失败{str(e)}")
        super().save_related(request, form, formsets, change)
