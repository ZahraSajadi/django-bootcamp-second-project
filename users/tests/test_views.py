from io import StringIO
import sys
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import OTP, Team
from users.views import (
    EnterOTPView,
    RequestOTPView,
    TeamCreateView,
    TeamDeleteView,
    TeamListView,
    TeamUpdateView,
    UserCreate,
    UserListView,
    UserUpdateView,
)
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
        expected_url = reverse("users:login_with_username") + "?next=" + self.url
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
        self.admin.is_staff = True
        self.admin.save()
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
        self.admin.is_staff = True
        self.admin.save()

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


class SignupViewTestCase(TestCase):
    def setUp(self) -> None:
        call_command("create_groups_and_permissions")
        self.factory = RequestFactory()

    def test_sign_up_get(self):
        request = self.factory.get(reverse("users:sign_up"))
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username:")
        self.assertContains(response, "Phone:")
        self.assertContains(response, "Email address:")
        self.assertContains(response, "Password:")
        self.assertContains(response, "Password confirmation:")

    def test_sign_up_post_correct_format(self):
        data = {
            "username": "admin",
            "email": "test@test.com",
            "phone": "09123456789",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="admin").exists())

    def test_sign_up_post_wrong_password_confirmation(self):
        data = {
            "username": "admin",
            "email": "test@test.com",
            "phone": "09123456789",
            "password1": "{9,x,zR;",
            "password2": "{9,x,z;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="admin").exists())

    def test_sign_up_post_wrong_phone_format(self):
        data = {
            "username": "admin",
            "email": "test@test.com",
            "phone": "0912345679",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="admin").exists())
        self.assertContains(response, "The phone number is wrong. The phone number must be 11 digits and start with 09")

    def test_sign_up_post_wrong_email_format(self):
        data = {
            "username": "admin",
            "email": "test@test",
            "phone": "09123456729",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="admin").exists())
        self.assertContains(response, "Enter a valid email address.")

    def test_sign_up_post_wrong_username_format(self):
        data = {
            "username": "admin%",
            "email": "test@test.com",
            "phone": "09123456729",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="admin%").exists())
        self.assertContains(
            response, "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."
        )

    def test_sign_up_post_taken_username(self):
        data = {
            "username": "admin",
            "email": "test@test.com",
            "phone": "09123456729",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        data = {
            "username": "admin",
            "email": "test1@test.com",
            "phone": "09121212121",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="test1@test.com").exists())
        self.assertContains(response, "A user with that username already exists.")

    def test_sign_up_post_taken_email(self):
        data = {
            "username": "admin",
            "email": "test@test.com",
            "phone": "09123456729",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        data = {
            "username": "admin1",
            "email": "test@test.com",
            "phone": "09121212121",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="admin1").exists())
        self.assertContains(response, "User with this Email address already exists.")

    def test_sign_up_post_taken_phone(self):
        data = {
            "username": "admin",
            "email": "test@test.com",
            "phone": "09123456729",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        data = {
            "username": "admin1",
            "email": "test1@test.com",
            "phone": "09123456729",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        request = self.factory.post(reverse("users:sign_up"), data)
        request.user = AnonymousUser()
        response = UserCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="test1@test.com").exists())
        self.assertContains(response, "User with this Phone already exists.")


class LoginViewTestCase(TestCase):
    def setUp(self) -> None:
        call_command("create_groups_and_permissions")
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="user",
            password="password",
            email="email@email.com",
            phone="09123456789",
        )
        self.middleware = SessionMiddleware(lambda x: None)
        self.stdout_orig = sys.stdout
        self.stderr_orig = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stdout = self.stdout_orig
        sys.stderr = self.stderr_orig

    def test_login_with_otp_email(self):
        data = {"email": self.user.email, "phone": ""}
        request = self.factory.post(reverse("users:login"), data)
        request.user = AnonymousUser()
        response = RequestOTPView.as_view()(request)
        self.assertEqual(response.__class__, HttpResponseRedirect)
        otp = OTP.objects.filter(user=self.user).order_by("-created_at").first()
        data["code"] = otp.otp
        request = self.factory.post(reverse("users:otp"), data)
        self.middleware.process_request(request)
        request.session.save()
        request.user = AnonymousUser()
        response = EnterOTPView.as_view()(request)
        self.assertEqual(response.__class__, HttpResponseRedirect)

    def test_login_with_otp_phone(self):
        data = {"email": "", "phone": self.user.phone}
        request = self.factory.post(reverse("users:login"), data)
        request.user = AnonymousUser()
        response = RequestOTPView.as_view()(request)
        self.assertEqual(response.__class__, HttpResponseRedirect)
        otp = OTP.objects.filter(user=self.user).order_by("-created_at").first()
        data["code"] = otp.otp
        request = self.factory.post(reverse("users:otp"), data)
        self.middleware.process_request(request)
        request.session.save()
        request.user = AnonymousUser()
        response = EnterOTPView.as_view()(request)
        self.assertEqual(response.__class__, HttpResponseRedirect)

    def test_login_with_otp_email_wrong_code(self):
        data = {"email": self.user.email, "phone": ""}
        request = self.factory.post(reverse("users:login"), data)
        request.user = AnonymousUser()
        response = RequestOTPView.as_view()(request)
        self.assertEqual(response.__class__, HttpResponseRedirect)
        data["code"] = "123456"
        request = self.factory.post(reverse("users:otp"), data)
        self.middleware.process_request(request)
        request.session.save()
        request.user = AnonymousUser()
        response = EnterOTPView.as_view()(request)
        self.assertEqual(response.status_code, 200)
