from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from .signals import delete_old_file

        pre_save.connect(delete_old_file, sender=get_user_model())
