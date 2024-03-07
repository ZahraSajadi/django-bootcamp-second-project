from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from .signals import (
            delete_old_file,
            add_superuser_to_custom_group,
            check_if_groups_exist,
        )

        pre_save.connect(delete_old_file, sender=get_user_model())
        pre_save.connect(check_if_groups_exist, sender=get_user_model())
        post_save.connect(add_superuser_to_custom_group, sender=get_user_model())
