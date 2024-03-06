from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Team


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
