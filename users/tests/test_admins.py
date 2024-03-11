from datetime import datetime, timedelta
from warnings import filterwarnings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from users.models import OTP, Team


filterwarnings("ignore", category=RuntimeWarning)
User = get_user_model()


class CustomUserAdminTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.super_user = User.objects.create_superuser(
            username="superuser",
            password="password",
            first_name="test_name",
            last_name="test_name",
            email="test@noemail.invalid",
            phone="09123456789",
        )
        self.user = User.objects.create_user(
            username="normaluser",
            password="password",
            first_name="test_name",
            last_name="test_name",
            email="test@email.invalid",
            phone="09133456789",
            is_active=False,
        )

    def test_custom_user_model_admin_list_display(self):
        self.client.login(username="superuser", password="password")
        response = self.client.get("/admin/users/customuser/")
        self.assertContains(response, "username")
        self.assertContains(response, "first_name")
        self.assertContains(response, "last_name")
        self.assertContains(response, "email")
        self.assertContains(response, "phone")
        self.assertContains(response, "team")
        self.assertContains(response, "is_active")

    def test_custom_user_model_admin_search(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get("/admin/users/customuser/?q=test")
        self.assertContains(response, self.super_user.username)
        response = self.client.get("/admin/users/customuser/?q=noemail")
        self.assertContains(response, self.super_user.username)
        response = self.client.get("/admin/users/customuser/?q=0912")
        self.assertContains(response, self.super_user.username)

    def test_custom_user_model_admin_filter(self):
        self.client.login(username=self.super_user.username, password="password")
        filter_params = {"is_active": True}
        response = self.client.get("/admin/users/customuser/", data=filter_params)
        self.assertContains(response, self.super_user.username)
        self.assertNotContains(response, self.user.username)

    def test_custom_user_model_admin_permissions(self):
        response = self.client.get("/admin/users/customuser/")
        self.assertEqual(response.status_code, 302)

        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.user.username, password="password")
        response = self.client.get("/admin/users/customuser/")
        self.assertEqual(response.status_code, 302)

    def test_custom_user_model_admin_fieldtest(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get(
            f"/admin/users/customuser/{self.super_user.id}/change/"
        )
        self.assertContains(response, "Username:")
        self.assertContains(response, "Password:")
        self.assertContains(response, "Profile image:")
        self.assertContains(response, "First name:")
        self.assertContains(response, "Last name:")
        self.assertContains(response, "Email address:")
        self.assertContains(response, "Phone:")
        self.assertContains(response, "Permissions")
        self.assertContains(response, "Last login:")
        self.assertContains(response, "Date joined:")
        self.assertContains(response, "Team:")


class TeamAdminTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.team1 = Team.objects.create(name="team_one")
        self.team2 = Team.objects.create(name="team_two")
        self.super_user = User.objects.create_superuser(
            username="superuser",
            password="password",
            first_name="test_name",
            last_name="test_name",
            email="test@noemail.invalid",
            phone="09123456789",
            team=self.team1,
        )
        self.user = User.objects.create_user(
            username="normaluser",
            password="password",
            first_name="test_name",
            last_name="test_name",
            email="test@email.invalid",
            phone="09133456789",
            is_active=False,
            team=self.team2,
        )

    def test_team_model_admin_list_display(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get("/admin/users/team/")
        self.assertContains(response, "name")
        self.assertContains(response, "member_count")

    def test_team_model_admin_search(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get("/admin/users/team/?q=one")
        self.assertContains(response, self.team1.name)
        self.assertNotContains(response, self.team2.name)

    def test_team_model_admin_fieldtest(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get(f"/admin/users/team/{self.team1.id}/change/")
        self.assertContains(response, "Name:")
        self.assertContains(response, self.team1)


class OTPAdminTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.super_user = User.objects.create_superuser(
            username="superuser",
            password="password",
            first_name="super",
            last_name="user",
            email="test@noemail.invalid",
            phone="09123456789",
        )
        self.user = User.objects.create_user(
            username="normaluser",
            password="password",
            first_name="test_name",
            last_name="test_name",
            email="test@email.invalid",
            phone="09133456789",
            is_active=False,
        )
        self.today = datetime.now()
        self.yesterday = self.today - timedelta(days=1)
        self.otp1 = OTP.objects.create(user=self.super_user, otp="123456")
        self.otp1.created_at = self.today
        self.otp1.save()
        self.otp2 = OTP.objects.create(user=self.user, otp="654321")
        self.otp2.created_at = self.yesterday
        self.otp2.save()

    def test_otp_model_admin_list_display(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get("/admin/users/otp/")
        self.assertContains(response, "user")
        self.assertContains(response, "otp")
        self.assertContains(response, "created_at")

    def test_otp_model_admin_filter(self):
        self.client.login(username=self.super_user.username, password="password")
        filter_params = {"user__id": self.super_user.id}
        response = self.client.get("/admin/users/otp/", data=filter_params)
        self.assertContains(response, self.otp1.otp)
        self.assertNotContains(response, self.otp2.otp)

        filter_params = {"created_at__gte": self.today}
        response = self.client.get("/admin/users/otp/", data=filter_params)
        self.assertContains(response, self.otp1.otp)
        self.assertNotContains(response, self.otp2.otp)

    def test_otpmodel_admin_fieldtest(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get(f"/admin/users/otp/{self.otp1.id}/change/")
        self.assertContains(response, "User:")
        self.assertContains(response, "Otp:")
        self.assertContains(response, self.otp1)
