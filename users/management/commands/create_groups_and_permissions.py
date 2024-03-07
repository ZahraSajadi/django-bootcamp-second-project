from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        team_leaders_group, created = Group.objects.get_or_create(name="Team Leaders")
        admins_group, created = Group.objects.get_or_create(name="Admins")

        # Team Leaders
        add_reservation_self_team = Permission.objects.get(codename="add_reservation_self_team")
        change_reservation_self_team = Permission.objects.get(codename="change_reservation_self_team")
        delete_reservation_self_team = Permission.objects.get(codename="delete_reservation_self_team")

        team_leaders_group.permissions.add(add_reservation_self_team)
        team_leaders_group.permissions.add(change_reservation_self_team)
        team_leaders_group.permissions.add(delete_reservation_self_team)

        # Admins
        can_add_team = Permission.objects.get(codename="add_team")
        can_change_team = Permission.objects.get(codename="change_team")
        can_delete_team = Permission.objects.get(codename="delete_team")
        can_view_team = Permission.objects.get(codename="view_team")
        can_view_team_list = Permission.objects.get(codename="view_team_list")

        can_add_room = Permission.objects.get(codename="add_room")
        can_change_room = Permission.objects.get(codename="change_room")
        can_delete_room = Permission.objects.get(codename="delete_room")
        can_view_room = Permission.objects.get(codename="view_room")
        can_view_room_list = Permission.objects.get(codename="view_room_list")

        can_add_reservation = Permission.objects.get(codename="add_reservation")
        can_delete_reservation = Permission.objects.get(codename="delete_reservation")
        can_view_reservation = Permission.objects.get(codename="view_reservation")
        can_view_reservation_list = Permission.objects.get(codename="view_reservation_list")

        can_view_customuser = Permission.objects.get(codename="view_customuser")
        can_change_customuser = Permission.objects.get(codename="change_customuser")
        can_view_user_list = Permission.objects.get(codename="view_customuser_list")

        admins_group.permissions.add(can_view_room_list)
        admins_group.permissions.add(can_view_reservation_list)
        admins_group.permissions.add(can_view_user_list)
        admins_group.permissions.add(can_view_team_list)
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
