import os

from django.contrib.auth.models import Group
from second_project.settings import ADMINS_GROUP_NAME, TEAM_LEADERS_GROUP_NAME


def delete_old_file(sender, instance, **kwargs):
    # on creation, signal callback won't be triggered
    if instance._state.adding and not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).profile_image
    except sender.DoesNotExist:
        return False
    if old_file and instance.profile_image and instance.profile_image.url != old_file.url:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)


def check_if_groups_exist(sender, instance, **kwargs):
    if not Group.objects.filter(name=ADMINS_GROUP_NAME).exists():
        raise Group.DoesNotExist(
            f"{ADMINS_GROUP_NAME} group doesn't exist please run create_groups_and_permissions command first."
        )


def add_superuser_to_custom_group(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        custom_group = Group.objects.get(name=ADMINS_GROUP_NAME)
        instance.groups.add(custom_group)


def team_pre_delete(sender, instance, **kwargs):
    team_leader_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
    team_leader = instance.customuser_set.filter(groups=team_leader_group).first()
    team_leader_group.user_set.remove(team_leader)
