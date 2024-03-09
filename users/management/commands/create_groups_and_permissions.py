from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from second_project.settings import ADMINS_GROUP_NAME, TEAM_LEADERS_GROUP_NAME
from reservation.models import Reservation

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            team_leaders_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
            team_leaders_group.delete()
        except Group.DoesNotExist:
            pass
        finally:
            team_leaders_group = Group.objects.create(name=TEAM_LEADERS_GROUP_NAME)
        try:
            admins_group = Group.objects.get(name=ADMINS_GROUP_NAME)
            admins_group.delete()
        except Group.DoesNotExist:
            pass
        finally:
            admins_group = Group.objects.create(name=ADMINS_GROUP_NAME)

        # Team Leaders
        reservation_content_type = ContentType.objects.get_for_model(Reservation)
        add_reservation_self_team = Permission.objects.filter(
            content_type_id=reservation_content_type.id,
            codename="add_reservation_self_team",
        ).first()
        delete_reservation_self_team = Permission.objects.filter(
            content_type_id=reservation_content_type.id,
            codename="delete_reservation_self_team",
        ).first()

        team_leaders_group.permissions.add(add_reservation_self_team)
        team_leaders_group.permissions.add(delete_reservation_self_team)

        # Admins
        can_add_team = Permission.objects.get(codename="add_team")
        can_change_team = Permission.objects.get(codename="change_team")
        can_delete_team = Permission.objects.get(codename="delete_team")
        can_view_team = Permission.objects.get(codename="view_team")

        can_add_room = Permission.objects.get(codename="add_room")
        can_change_room = Permission.objects.get(codename="change_room")
        can_delete_room = Permission.objects.get(codename="delete_room")
        can_view_room = Permission.objects.get(codename="view_room")

        can_add_reservation = Permission.objects.get(codename="add_reservation")
        can_delete_reservation = Permission.objects.get(codename="delete_reservation")
        can_view_reservation = Permission.objects.get(codename="view_reservation")

        can_view_customuser = Permission.objects.get(codename="view_customuser")
        can_change_customuser = Permission.objects.get(codename="change_customuser")

        admins_group.permissions.add(can_add_team)
        admins_group.permissions.add(can_change_team)
        admins_group.permissions.add(can_delete_team)
        admins_group.permissions.add(can_view_team)
        admins_group.permissions.add(can_add_room)
        admins_group.permissions.add(can_change_room)
        admins_group.permissions.add(can_delete_room)
        admins_group.permissions.add(can_view_room)
        admins_group.permissions.add(can_add_reservation)
        admins_group.permissions.add(can_delete_reservation)
        admins_group.permissions.add(can_view_reservation)
        admins_group.permissions.add(can_change_customuser)
        admins_group.permissions.add(can_view_customuser)

        for user in User.objects.all():
            if user.is_staff or user.is_superuser:
                user.save()
