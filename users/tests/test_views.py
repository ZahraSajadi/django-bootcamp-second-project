from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import Team
from users.views import TeamCreateView, TeamDeleteView, TeamListView, TeamUpdateView, UserListView, UserUpdateView
from second_project.settings import ADMINS_GROUP_NAME, TEAM_LEADERS_GROUP_NAME

User = get_user_model()


class ProfileViewTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.url = reverse("users:profile")

    def test_profile_view_authenticated(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertEqual(response.context["user"], self.user)

    def test_profile_view_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        expected_url = reverse("users:login") + "?next=" + self.url
        self.assertRedirects(response, expected_url)


class PasswordUpdateViewTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.url = reverse("users:change_password")

    def test_password_change_view(self):
        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/change_password.html")

    def test_password_change_view_post(self):
        self.client.login(username="testuser", password="testpassword")
        data = {
            "old_password": "testpassword",
            "new_password1": "newtestpassword",
            "new_password2": "newtestpassword",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newtestpassword"))


class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.url = reverse("users:profile_update")
        # self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
            first_name="John",
            last_name="Doe",
            email="testuser@example.com",
            phone="1234567890",
        )

    def test_profile_update_view(self):
        # request = self.factory.get(self.url)
        # request.user = self.user
        # response = ProfileUpdateView.as_view()(request)

        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile_update.html")

    def test_profile_update_view_post(self):
        # request = self.factory.post(self.url, new_data)
        # request.user = self.user
        # response = ProfileUpdateView.as_view()(request)

        self.client.login(username="testuser", password="testpassword")
        new_data = {
            "username": "newusername",
            "first_name": "New",
            "last_name": "User",
            "email": "newemail@example.com",
            "phone": "09126547896",
        }
        response = self.client.post(self.url, new_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:profile"))

        updated_user = get_user_model().objects.get(id=self.user.id)
        self.assertEqual(updated_user.username, new_data["username"])
        self.assertEqual(updated_user.first_name, new_data["first_name"])
        self.assertEqual(updated_user.last_name, new_data["last_name"])
        self.assertEqual(updated_user.email, new_data["email"])
        self.assertEqual(updated_user.phone, new_data["phone"])


class TeamManagementViewsTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.factory = RequestFactory()
        self.admin = User.objects.create_user(username="admin", password="password")
        self.user = User.objects.create_user(
            username="user",
            password="password",
            email="empty",
            phone="empty",
        )
        self.admins_group = Group.objects.get(name=ADMINS_GROUP_NAME)
        self.admins_group.user_set.add(self.admin)
        self.team = Team.objects.create(name="Test Team")

    def test_team_list_view_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get(reverse("users:team_list"))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            TeamListView.as_view()(request)

    def test_team_create_view_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get(reverse("users:team_create"))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            TeamCreateView.as_view()(request)

    def test_team_update_view_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get(reverse("users:team_update", kwargs={"pk": self.team.id}))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            TeamUpdateView.as_view()(request)

    def test_team_delete_view_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get(reverse("users:team_delete", kwargs={"pk": self.team.id}))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            TeamDeleteView.as_view()(request)

    def test_team_list_view_admin_user(self):
        self.client.login(username=self.admin.username, password="password")
        request = self.factory.get(reverse("users:team_list"))
        request.user = self.admin
        request.session = self.client.session
        response = TeamListView.as_view()(request)
        self.assertContains(response, self.team)

    def test_team_create_view_admin_user(self):
        self.client.login(username=self.admin.username, password="password")
        team_name = "New Team"
        data = {"name": team_name, "members": [self.admin.id, self.user.id]}
        request = self.factory.post(reverse("users:team_create"), data)
        request.user = self.admin
        request.session = self.client.session
        response = TeamCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Team.objects.filter(name=team_name).exists())
        self.assertEqual(team_name, User.objects.get(pk=self.admin.id).team.name)
        self.assertEqual(team_name, User.objects.get(pk=self.user.id).team.name)

    def test_team_update_view_admin_user(self):
        self.client.login(username=self.admin.username, password="password")
        team_name = "New Team"
        data = {"name": team_name, "leader": self.admin.id, "members": [self.user.id]}
        request = self.factory.post(reverse("users:team_update", kwargs={"pk": self.team.id}), data)
        request.user = self.admin
        request.session = self.client.session
        response = TeamUpdateView.as_view()(request, pk=self.team.id)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Team.objects.filter(name=team_name).exists())
        self.assertFalse(Team.objects.filter(name=self.team.name).exists())
        self.assertEqual(team_name, User.objects.get(pk=self.user.id).team.name)
        self.assertEqual(team_name, User.objects.get(pk=self.admin.id).team.name)
        team_leader_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
        self.assertIn(team_leader_group, User.objects.get(pk=self.admin.id).groups.all())

    def test_team_delete_view_admin_user(self):
        self.client.login(username=self.admin.username, password="password")
        data = {"name": self.team.name, "leader": self.admin.id, "members": [self.user.id]}
        request = self.factory.post(reverse("users:team_update", kwargs={"pk": self.team.id}), data)
        request.user = self.admin
        request.session = self.client.session
        response = TeamUpdateView.as_view()(request, pk=self.team.id)
        request = self.factory.post(reverse("users:team_delete", kwargs={"pk": self.team.id}))
        request.user = self.admin
        request.session = self.client.session
        response = TeamDeleteView.as_view()(request, pk=self.team.id)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Team.objects.filter(name=self.team.name).exists())
        self.assertIsNone(User.objects.get(pk=self.user.id).team)
        self.assertIsNone(User.objects.get(pk=self.admin.id).team)
        team_leader_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
        self.assertNotIn(team_leader_group, User.objects.get(pk=self.admin.id).groups.all())


class UserManagementViewTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.factory = RequestFactory()
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
        request = self.factory.get(reverse("users:user_list"))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            UserListView.as_view()(request)

    def test_user_update_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get(reverse("users:user_list"))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            UserUpdateView.as_view()(request, pk=self.user.id)

    def test_user_list_admin_user(self):
        self.client.login(username=self.admin.username, password="password")
        request = self.factory.get(reverse("users:user_list"))
        request.user = self.admin
        request.session = self.client.session
        response = UserListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

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
        request = self.factory.post(reverse("users:user_update", kwargs={"pk": self.user.id}), data)
        request.user = self.superuser
        request.session = self.client.session
        response = UserUpdateView.as_view()(request, pk=self.user.id)
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
        request = self.factory.post(reverse("users:user_update", kwargs={"pk": self.user.id}), data)
        request.user = self.superuser
        request.session = self.client.session
        response = UserUpdateView.as_view()(request, pk=self.user.id)
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
        request = self.factory.post(reverse("users:user_update", kwargs={"pk": self.user.id}), data)
        request.user = self.admin
        request.session = self.client.session
        response = UserUpdateView.as_view()(request, pk=self.user.id)
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
        request = self.factory.post(reverse("users:user_update", kwargs={"pk": self.user.id}), data)
        request.user = self.admin
        request.session = self.client.session
        response = UserUpdateView.as_view()(request, pk=self.user.id)
        self.assertEqual(response.status_code, 403)
