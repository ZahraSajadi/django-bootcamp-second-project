from io import StringIO
import sys
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from reservation.models import Reservation, Room
from users.models import Team

User = get_user_model()


class YourCommandTestCase(TestCase):
    def setUp(self) -> None:
        call_command("create_groups_and_permissions")
        self.room = Room.objects.create(name="Room1", capacity=10)
        self.room_deactive = Room.objects.create(name="Room1", capacity=10, is_active=False)
        self.team = Team.objects.create(name="Team")
        self.user1 = User.objects.create_user(
            username="user1", password="password", email="asfasf@asd.com", team=self.team
        )
        self.user2 = User.objects.create_user(username="user2", password="password", email="123@asd.com", phone="123")
        self.reservation1 = Reservation.objects.create(
            room=self.room,
            reserver_user=self.user1,
            team=self.team,
            start_date=timezone.now() + timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=3),
        )
        self.reservation2 = Reservation.objects.create(
            room=self.room,
            reserver_user=self.user1,
            team=self.team,
            start_date=timezone.now() + timezone.timedelta(hours=3),
            end_date=timezone.now() + timezone.timedelta(hours=4),
        )
        self.reservation3 = Reservation.objects.create(
            room=self.room_deactive,
            reserver_user=self.user1,
            team=self.team,
            start_date=timezone.now() + timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=3),
        )

    def test_command_execution(self):
        out = StringIO()
        sys.stdout = out
        call_command("reservation_email_reminder")
        output = out.getvalue().strip()
        sys.stdout = sys.__stdout__
        self.assertIn("1 reminder email sent.", output)
        self.assertIn("1 cancellation email sent.", output)
