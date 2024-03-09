from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete, pre_save


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from .signals import (
            delete_old_file,
            add_superuser_to_custom_group,
            check_if_groups_exist,
            team_pre_delete,
            update_staff_user_group,
        )
        from .models import Team

        User = get_user_model()
        pre_save.connect(delete_old_file, sender=User)
        pre_save.connect(check_if_groups_exist, sender=User)
        post_save.connect(add_superuser_to_custom_group, sender=User)
        post_save.connect(update_staff_user_group, sender=User)
        pre_delete.connect(team_pre_delete, sender=Team)
