import random
from django.core.validators import RegexValidator
from django.utils import timezone

phone_regex = RegexValidator(
    regex=r"^09\d{9}$",
    message="The phone number is wrong. The phone number must be 11 digits and start with 09",
)


def generate_otp(length=6):
    otp = "".join(random.choices("0123456789", k=length))
    return otp


def user_image_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"profile_images/user_{instance.id}.{ext}"


def verify_otp(otp, code):
    if timezone.now() - otp.created_at <= timezone.timedelta(minutes=2):
        if otp.otp == code:
            otp.delete()
            return True
    else:
        otp.delete()
    return False
