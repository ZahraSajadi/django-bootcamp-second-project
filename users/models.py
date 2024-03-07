from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

from utils.db.model_helper import generate_otp, phone_regex, user_image_path


class CustomUser(AbstractUser):
    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150)
    email = models.EmailField("email address", unique=True)
    profile_image = models.ImageField(upload_to=user_image_path, blank=True, null=True)
    phone = models.CharField(max_length=11, validators=[phone_regex], unique=True)
    team = models.ForeignKey("Team", on_delete=models.PROTECT, null=True, blank=True)
    REQUIRED_FIELDS = ["first_name", "last_name", "email", "phone"]

    class Meta:
        permissions = [
            ("add_reservation_self_team", "Can add reservation to their team"),
            ("delete_reservation_self_team", "Can delete reservation of their team"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_team_leader(self):
        return self.groups.filter(name="Team Leader").exists()

    @property
    def is_admin(self):
        return self.groups.filter(name="Admins").exists()


class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OTP(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default=generate_otp)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - OTP: {self.otp}"
