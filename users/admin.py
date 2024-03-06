from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import OTP, Team

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
        "team",
        "is_active",
    )
    search_fields = ("username__icontains", "email__icontains", "phone__contains")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Image", {"fields": ("profile_image",)}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "phone")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("User Team", {"fields": ("team",)}),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "member_count")
    search_fields = ("name__icontains",)

    def member_count(self, obj):
        return obj.customuser_set.count()

    member_count.short_description = "Member Count"


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "created_at")
    list_filter = ("user", "created_at")
