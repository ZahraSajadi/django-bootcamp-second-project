from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import Team
from second_project.settings import ADMINS_GROUP_NAME

User = get_user_model()


class TeamManagementTemplateTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.user = User.objects.create_user(username="user", password="password")
        self.admin = User.objects.create_user(
            username="admin",
            password="password",
            email="empty",
            phone="empty",
        )
        self.admins_group = Group.objects.get(name=ADMINS_GROUP_NAME)
        self.admins_group.user_set.add(self.admin)
        self.team = Team.objects.create(name="Test Team")

    def test_team_list_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("users:team_list"))
        self.assertEqual(response.status_code, 403)

    def test_team_create_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("users:team_create"))
        self.assertEqual(response.status_code, 403)

    def test_team_update_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("users:team_update", kwargs={"pk": self.team.id}))
        self.assertEqual(response.status_code, 403)

    def test_team_delete_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("users:team_delete", kwargs={"pk": self.team.id}))
        self.assertEqual(response.status_code, 403)

    def test_team_list_template(self):
        self.client.login(username=self.admin.username, password="password")
        response = self.client.get(reverse("users:team_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.team)
        self.assertTemplateUsed(response, "users/team_list.html")

    def test_team_create_template(self):
        self.client.login(username=self.admin.username, password="password")
        response = self.client.get(reverse("users:team_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/team_create.html")

    def test_team_update_template(self):
        self.client.login(username=self.admin.username, password="password")
        response = self.client.get(reverse("users:team_update", args=[self.team.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.team)
        self.assertTemplateUsed(response, "users/team_update.html")

    def test_team_create(self):
        self.client.login(username=self.admin.username, password="password")
        team_name = "New Team"
        data = {"name": team_name, "members": [self.admin.pk, self.user.pk]}
        self.client.post(reverse("users:team_create"), data)
        self.assertTrue(Team.objects.filter(name=team_name).exists())
        for user in User.objects.filter(team__name=team_name).all():
            self.assertEqual(team_name, user.team.name)

    def test_team_update(self):
        self.client.login(username=self.admin.username, password="password")
        new_team_name = "New Team Name"
        data = {"name": new_team_name, "members": [self.admin.pk]}
        self.client.post(reverse("users:team_update", kwargs={"pk": self.team.id}), data)
        self.assertTrue(Team.objects.filter(name=new_team_name).exists())
        self.assertFalse(Team.objects.filter(name=self.team.name).exists())
        user = User.objects.get(pk=self.admin.pk)
        self.assertEqual(new_team_name, user.team.name)
        user = User.objects.get(pk=self.user.pk)
        self.assertIsNone(user.team)

    def test_team_delete(self):
        self.client.login(username=self.admin.username, password="password")
        self.assertTrue(Team.objects.filter(name=self.team.name).exists())
        self.client.post(reverse("users:team_delete", kwargs={"pk": self.team.id}))
        self.assertFalse(Team.objects.filter(name=self.team.name).exists())


class UserManagementTemplateTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.superuser = User.objects.create_superuser(username="superuser", password="password")
        self.admin = User.objects.create_user(
            username="admin",
            password="password",
            email="empty",
            phone="empty",
        )
        self.user = User.objects.create_user(
            username="normal",
            password="password",
            email="empty1",
            phone="empty1",
        )
        self.admins_group = Group.objects.get(name=ADMINS_GROUP_NAME)
        self.admin.is_staff = True
        self.admin.save()
        self.admins_group.user_set.add(self.admin)

    def test_user_list_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("users:user_list"))
        self.assertEqual(response.status_code, 403)

    def test_user_update_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("users:user_update", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 403)

    def test_user_list_template(self):
        self.client.login(username=self.admin.username, password="password")
        response = self.client.get(reverse("users:user_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user)
        self.assertContains(response, self.admin)
        self.assertContains(response, self.superuser)
        self.assertTemplateUsed(response, "users/user_list.html")

    def test_user_update_template_admin(self):
        self.client.login(username=self.admin.username, password="password")
        response = self.client.get(reverse("users:user_update", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user)
        self.assertNotContains(response, "Staff status:")
        self.assertTemplateUsed(response, "users/profile_update.html")

    def test_user_update_template_superuser(self):
        self.client.login(username=self.superuser.username, password="password")
        response = self.client.get(reverse("users:user_update", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user)
        self.assertContains(response, "Staff status:")
        self.assertTemplateUsed(response, "users/profile_update.html")
        response = self.client.get(reverse("users:user_update", args=[self.superuser.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.superuser)
        self.assertNotContains(response, "Staff status:")

    def test_user_update_superuser(self):
        self.client.login(username=self.superuser.username, password="password")
        new_first_name = "New First Name"
        new_last_name = "New Last Name"
        data = {
            "username": self.user.username,
            "email": "test@test.com",
            "phone": "09123456789",
            "first_name": new_first_name,
            "last_name": new_last_name,
        }
        response = self.client.post(reverse("users:user_update", kwargs={"pk": self.user.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(first_name=new_first_name).exists())
        self.assertTrue(User.objects.filter(last_name=new_last_name).exists())
        data = {
            "username": self.user.username,
            "email": "test@test.com",
            "phone": "09123456789",
            "first_name": new_first_name,
            "last_name": new_last_name,
            "is_staff": "on",
        }
        response = self.client.post(reverse("users:user_update", kwargs={"pk": self.user.id}), data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(pk=self.user.id)
        self.assertTrue(user.is_staff)
        self.assertIn(ADMINS_GROUP_NAME, self.user.groups.values_list("name", flat=True))

    def test_user_update_admin(self):
        self.client.login(username=self.admin.username, password="password")
        new_first_name = "New First Name"
        new_last_name = "New Last Name"
        data = {
            "username": self.user.username,
            "email": "test@test.com",
            "phone": "09123456789",
            "first_name": new_first_name,
            "last_name": new_last_name,
        }
        response = self.client.post(reverse("users:user_update", kwargs={"pk": self.user.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(first_name=new_first_name).exists())
        self.assertTrue(User.objects.filter(last_name=new_last_name).exists())
        data = {
            "username": self.user.username,
            "email": "test@test.com",
            "phone": "09123456789",
            "first_name": new_first_name,
            "last_name": new_last_name,
            "is_staff": "on",
        }
        response = self.client.post(reverse("users:user_update", kwargs={"pk": self.user.id}), data)
        self.assertEqual(response.status_code, 403)
