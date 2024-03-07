from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test.client import Client

User = get_user_model()


class ProfileViewTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.url = reverse("users:profile")

    def test_profile_view_authenticated(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")
        self.assertEqual(response.context["user"], self.user)

    def test_profile_view_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        expected_url = reverse("users:login") + "?next=" + self.url
        self.assertRedirects(response, expected_url)


class PasswordUpdateViewTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.url = reverse("users:change_password")

    def test_password_change_view(self):
        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "change_password.html")

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
        self.client = Client()
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
        self.assertTemplateUsed(response, "profile_update.html")

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
