from io import StringIO
import sys
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from users.models import OTP, Team
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
        self.admin.is_staff = True
        self.admin.save()
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


class SignupTemplateTestCase(TestCase):
    def setUp(self) -> None:
        call_command("create_groups_and_permissions")

    def test_sign_up_get(self):
        response = self.client.get(reverse("users:sign_up"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username:")
        self.assertContains(response, "Phone:")
        self.assertContains(response, "Email address:")
        self.assertContains(response, "Password:")
        self.assertContains(response, "Password confirmation:")
        self.assertTemplateUsed("users/signup.html")

    def test_sign_up_post_correct_format(self):
        data = {
            "username": "admin",
            "email": "test@test.com",
            "phone": "09123456789",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        response = self.client.post(reverse("users:sign_up"), data)
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
        response = self.client.post(reverse("users:sign_up"), data)
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
        response = self.client.post(reverse("users:sign_up"), data)
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
        response = self.client.post(reverse("users:sign_up"), data)
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
        response = self.client.post(reverse("users:sign_up"), data)
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
        response = self.client.post(reverse("users:sign_up"), data)
        data = {
            "username": "admin",
            "email": "test1@test.com",
            "phone": "09121212121",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        response = self.client.post(reverse("users:sign_up"), data)
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
        response = self.client.post(reverse("users:sign_up"), data)
        data = {
            "username": "admin1",
            "email": "test@test.com",
            "phone": "09121212121",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        response = self.client.post(reverse("users:sign_up"), data)
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
        response = self.client.post(reverse("users:sign_up"), data)
        data = {
            "username": "admin1",
            "email": "test1@test.com",
            "phone": "09123456729",
            "password1": "{9,x,zR;",
            "password2": "{9,x,zR;",
        }
        response = self.client.post(reverse("users:sign_up"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="test1@test.com").exists())
        self.assertContains(response, "User with this Phone already exists.")


class LoginTemplateTestCase(TestCase):
    def setUp(self) -> None:
        call_command("create_groups_and_permissions")
        self.user = User.objects.create_user(
            username="user",
            password="password",
            email="email@email.com",
            phone="09123456789",
        )
        self.stdout_orig = sys.stdout
        self.stderr_orig = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stdout = self.stdout_orig
        sys.stderr = self.stderr_orig

    def test_login_page(self):
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email:")
        self.assertContains(response, "Phone:")
        self.assertTemplateUsed("users/login.html")

    def test_login_with_username_page(self):
        response = self.client.get(reverse("users:login_with_username"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username:")
        self.assertContains(response, "Password:")
        self.assertTemplateUsed("users/login.html")

    def test_otp_page(self):
        response = self.client.get(reverse("users:otp"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Code:")
        self.assertContains(response, "Time remaining:")
        self.assertTemplateUsed("users/login.html")

    def test_login_with_username(self):
        data = {"username": self.user.username, "password": "password"}
        response = self.client.post(reverse("users:login_with_username"), data)
        self.assertRedirects(response, reverse_lazy("index"))
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Upcoming")

    def test_login_with_username_wrong_password(self):
        data = {"username": self.user.username, "password": "p"}
        response = self.client.post(reverse("users:login_with_username"), data)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("index"))
        self.assertRedirects(response, reverse_lazy("users:login_with_username") + "?next=/")

    def test_login_with_otp_email(self):
        data = {"email": self.user.email, "phone": ""}
        response = self.client.post(reverse("users:login"), data)
        self.assertRedirects(response, reverse_lazy("users:otp") + f'?email={data["email"]}&phone={data["phone"]}')
        otp = OTP.objects.filter(user=self.user).order_by("-created_at").first()
        data["code"] = otp.otp
        response = self.client.post(reverse("users:otp"), data)
        self.assertRedirects(response, reverse_lazy("index"))
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Upcoming")

    def test_login_with_otp_phone(self):
        data = {"email": "", "phone": self.user.phone}
        response = self.client.post(reverse("users:login"), data)
        self.assertRedirects(response, reverse_lazy("users:otp") + f'?email={data["email"]}&phone={data["phone"]}')
        otp = OTP.objects.filter(user=self.user).order_by("-created_at").first()
        data["code"] = otp.otp
        response = self.client.post(reverse("users:otp"), data)
        self.assertRedirects(response, reverse_lazy("index"))
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Upcoming")

    def test_login_with_otp_email_wrong_code(self):
        data = {"email": self.user.email, "phone": ""}
        response = self.client.post(reverse("users:login"), data)
        self.assertRedirects(response, reverse_lazy("users:otp") + f'?email={data["email"]}&phone={data["phone"]}')
        data["code"] = "123456"
        response = self.client.post(reverse("users:otp"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OTP wrong or expired, please try again")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 302)
