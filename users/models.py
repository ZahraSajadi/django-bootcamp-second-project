from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

from utils.db.model_helper import random_password


class CustomUser(AbstractUser):
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    phone = models.CharField(max_length=11)
    team = models.ForeignKey("Team", on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OTP(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default=random_password)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - OTP: {self.otp}"
