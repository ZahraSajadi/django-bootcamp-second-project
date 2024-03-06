from django.test import TestCase
from users.models import CustomUser


class CustomUserAdminTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="password",
            first_name="test_name",
            last_name="test_name",
            email="test@noemail.invalid",
        )
