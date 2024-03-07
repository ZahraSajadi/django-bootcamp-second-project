from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from reservation.models import Reservation, Room
from users.models import Team

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        team_leaders_group, created = Group.objects.get_or_create(name="Team Leaders")
        admins_group, created = Group.objects.get_or_create(name="Admins")

        # Team Leaders
        content_type = ContentType.objects.get_for_model(Reservation)
        add_reservation_self_team, created = Permission.objects.get_or_create(
            name="Can add reservation to their team",
            codename="add_reservation_self_team",
            content_type=content_type,
        )
        change_reservation_self_team, created = Permission.objects.get_or_create(
            name="Can change reservation of their team",
            codename="change_reservation_self_team",
            content_type=content_type,
        )
        delete_reservation_self_team, created = Permission.objects.get_or_create(
            name="Can delete reservation of their team",
            codename="delete_reservation_self_team",
            content_type=content_type,
        )
        team_leaders_group.permissions.add(add_reservation_self_team)
        team_leaders_group.permissions.add(change_reservation_self_team)
        team_leaders_group.permissions.add(delete_reservation_self_team)

        # Admins
        content_type = ContentType.objects.get_for_model(Room)
        can_view_room_list, created = Permission.objects.get_or_create(
            name="Can view rooms list",
            codename="view_room_list",
            content_type=content_type,
        )
        content_type = ContentType.objects.get_for_model(Reservation)
        can_view_reservation_list, created = Permission.objects.get_or_create(
            name="Can view reservations list",
            codename="view_reservation_list",
            content_type=content_type,
        )
        content_type = ContentType.objects.get_for_model(User)
        can_view_user_list, created = Permission.objects.get_or_create(
            name="Can view users list",
            codename="view_user_list",
            content_type=content_type,
        )
        content_type = ContentType.objects.get_for_model(Team)
        can_view_team_list, created = Permission.objects.get_or_create(
            name="Can view teams list",
            codename="view_team_list",
            content_type=content_type,
        )

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
