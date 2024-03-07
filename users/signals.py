import os


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
