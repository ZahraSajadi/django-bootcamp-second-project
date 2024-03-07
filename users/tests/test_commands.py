from django.core.management import call_command
from django.contrib.auth.models import Group, Permission
from django.test import TestCase


class YourCommandTestCase(TestCase):
    def test_command_execution(self):
        call_command("create_groups_and_permissions")

        team_leaders_group = Group.objects.get(name="Team Leaders")
        self.assertIsNotNone(team_leaders_group)

        admins_group = Group.objects.get(name="Admins")
        self.assertIsNotNone(admins_group)

        add_reservation_perm = Permission.objects.get(codename="add_reservation_self_team")
        delete_reservation_perm = Permission.objects.get(codename="delete_reservation_self_team")

        self.assertIn(add_reservation_perm, team_leaders_group.permissions.all())
        self.assertIn(delete_reservation_perm, team_leaders_group.permissions.all())

        admin_permissions = [
            "add_team",
            "change_team",
            "delete_team",
            "view_team",
            "add_room",
            "change_room",
            "delete_room",
            "view_room",
            "delete_reservation",
            "view_reservation",
            "view_customuser",
            "change_customuser",
        ]

        for perm_codename in admin_permissions:
            permission = Permission.objects.get(codename=perm_codename)
            self.assertIn(permission, admins_group.permissions.all())
