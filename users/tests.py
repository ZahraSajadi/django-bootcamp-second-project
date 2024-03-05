from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Team, OTP, CustomUserManager

User = get_user_model()


class CustomUserManagerTestCase(TestCase):
    def setUp(self):
        self.manager = CustomUserManager()

    def test_create_user_with_email(self):
        user = self.manager.create_user(
            email="test@example.com", first_name="John", last_name="Doe", team=None
        )

        self.assertIsNotNone(user, "User should be created successfully")

        self.assertEqual(
            user.email, "test@example.com", "User email should be set correctly"
        )

        self.assertEqual(
            user.first_name, "John", "User first name should be set correctly"
        )
        self.assertEqual(
            user.last_name, "Doe", "User last name should be set correctly"
        )

        self.assertFalse(user.has_usable_password(), "User password should not be set")

    def test_create_user_missing_email(self):
        with self.assertRaises(ValueError):
            self.manager.create_user(email="", first_name="Jane", last_name="Smith")


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Test Team")

    def test_create_custom_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="09123456789",
            team=self.team,
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.phone, "09123456789")
        self.assertEqual(user.team, self.team)


class TeamModelTest(TestCase):
    def test_create_team(self):
        team = Team.objects.create(name="Test Team")
        self.assertEqual(team.name, "Test Team")


class OTPModelTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="123456789",
            team=None,
        )

        # Create an OTP instance
        self.otp = OTP.objects.create(user=self.user, otp="123456")

    def test_otp_model(self):
        # Retrieve the OTP instance created in setUp
        otp = OTP.objects.get(user=self.user)

        # Check if the OTP instance was created successfully
        self.assertEqual(otp.otp, "123456")
        self.assertEqual(otp.user, self.user)
