import os

from django.contrib.auth.models import Group


def delete_old_file(sender, instance, **kwargs):
    # on creation, signal callback won't be triggered
    if instance._state.adding and not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).profile_image
    except sender.DoesNotExist:
        return False
    if (
        old_file
        and instance.profile_image
        and instance.profile_image.url != old_file.url
    ):
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)


def check_if_groups_exist(sender, instance, **kwargs):
    if not Group.objects.filter(name="Admins").exists():
        raise Group.DoesNotExist(
            "Admins group doesn't exist please run create_groups_and_permissions command first."
        )


def add_superuser_to_custom_group(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        custom_group = Group.objects.get(name="Admins")
        instance.groups.add(custom_group)
