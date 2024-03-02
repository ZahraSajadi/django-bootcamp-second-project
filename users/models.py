from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    phone_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message='شماره تلفن وارد شده معتبر نیست.'
    )
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phone = models.CharField(max_length=11, validators=[phone_validator])
    team = models.ForeignKey('Team', on_delete=models.PROTECT, null=True)


class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
