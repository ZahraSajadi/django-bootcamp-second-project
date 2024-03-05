from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from users.models import Team, OTP

User = get_user_model()


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Test Team")
        self.user = User.objects.create_user(
            username="TestUser",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="09123456789",
            team=self.team,
        )

    def test_create_custom_user(self):
        self.assertEqual(self.user.username, "TestUser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.phone, "09123456789")
        self.assertEqual(self.user.team, self.team)

    def test_phone_number_validation(self):
        # Test valid phone number
        self.user.full_clean()  # Validate the model instance

        # Test invalid phone number (less than 11 digits)
        with self.assertRaises(ValidationError):
            User(username="testuser", phone="0912345678", team=self.team).full_clean()

        # Test invalid phone number (more than 11 digits)
        with self.assertRaises(ValidationError):
            User(username="testuser", phone="091234567890", team=self.team).full_clean()

        # Test invalid phone number (does not start with 09)
        with self.assertRaises(ValidationError):
            User(username="testuser", phone="08123456789", team=self.team).full_clean()

    def test_user_str_representation(self):
        self.assertEqual(str(self.user), "John Doe")


class TeamModelTest(TestCase):
    def test_create_team(self):
        team = Team.objects.create(name="Test Team")
        self.assertEqual(team.name, "Test Team")


class OTPModelTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = get_user_model().objects.create_user(
            username="Test User",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="123456789",
            team=None,
        )

        # Create an OTP instance
        self.otp = OTP.objects.create(user=self.user, otp="123456")

    def test_otp_model(self):
        otp = OTP.objects.filter(user=self.user).order_by("-created_at").first()

        # Check if the OTP instance was created successfully
        self.assertEqual(otp.otp, "123456")
        self.assertEqual(otp.user, self.user)

    def test_otp_generation(self):
        otp_instance = OTP(user=self.user)
        otp_instance.save()

        self.assertEqual(len(otp_instance.otp), 6)  # Check OTP length
        self.assertTrue(otp_instance.otp.isdigit())  # Check OTP is numeric
