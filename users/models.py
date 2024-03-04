from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = get_user_model()(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(None)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    email = models.EmailField(help_text="email address", unique=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    phone = models.CharField(max_length=11)
    team = models.ForeignKey("Team", on_delete=models.PROTECT, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OTP(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - OTP: {self.otp}"
