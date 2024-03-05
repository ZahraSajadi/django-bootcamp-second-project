from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import OTP, Team


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone", "team", "is_active")
    list_filter = ("is_active",)
    search_fields = ("username__icontains", "email__icontains")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name__icontains",)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "created_at")
    list_filter = ("user", "created_at")
