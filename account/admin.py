from django.contrib import admin
from .models import User
# Register your models here.


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ("nickname", "email")
    search_fields = ("nickname", "email")
