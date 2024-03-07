from datetime import date
from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from reservation.models import Reservation, Room, Rating, Comment
from users.models import Team


class RoomModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("create_groups_and_permissions")
        # Set up non-modified objects used by all test methods
        Room.objects.create(
            name="Room 1", capacity=3, description="Test room 1", is_active=True
        )
        Room.objects.create(
            name="Room 2", capacity=5, description="Test room 2", is_active=False
        )

    def test_str_representation(self):
        room = Room.objects.get(name="Room 1")
        self.assertEqual(str(room), "Room 1")

    def test_capacity_positive(self):
        room = Room.objects.get(name="Room 1")
        self.assertTrue(room.capacity > 0)

    def test_status_default_value(self):
        room = Room.objects.get(name="Room 1")
        self.assertTrue(room.is_active)

    def test_name_max_length(self):
        room = Room.objects.get(name="Room 1")
        max_length = room._meta.get_field("name").max_length
        self.assertLessEqual(len(room.name), max_length)

    def test_capacity_validation(self):
        # Test valid rating value
        room = Room.objects.create(name="Room 3", capacity=5, description="Test room 3")
        room.full_clean()

        # Test invalid rating value (less than 1)
        with self.assertRaises(ValidationError):
            Room.objects.create(
                name="Room 3", capacity=0, description="Test room 3"
            ).full_clean()


class ReservationModelTest(TestCase):
    @classmethod
    def setUp(self):
        call_command("create_groups_and_permissions")
        # Set up non-modified objects used by all test methods
        self.room = Room.objects.create(
            name="Test Room", capacity=5, description="Test room", is_active=True
        )
        self.team = Team.objects.create(name="Test Team")
        self.user = get_user_model().objects.create_user(
            username="TestUser",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="123456789",
            team=self.team,
        )

        self.reservation = Reservation.objects.create(
            room=self.room,
            reserver_user=self.user,
            team=self.team,
            start_date="2024-01-01 10:00:00",
            end_date="2024-01-01 11:00:00",
            note="Test note",
        )
        self.reservation2 = Reservation.objects.create(
            room=self.room,
            reserver_user=self.user,
            team=self.team,
            start_date="2024-01-02 10:00:00",
            end_date="2024-01-01 11:00:00",
        )

    def test_room_field(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertEqual(reservation.room, self.room)

    def test_room_foreign_key(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertIsInstance(reservation.room, Room)

    def test_user_field(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertEqual(reservation.reserver_user, self.user)

    def test_user_foreign_key(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertIsInstance(reservation.reserver_user, get_user_model())

    def test_team_field(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertEqual(reservation.team, self.team)

    def test_team_foreign_key(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertIsNotNone(reservation.team)

    def test_start_date_field(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertEqual(
            reservation.start_date.strftime("%Y-%m-%d %H:%M:%S"), "2024-01-01 10:00:00"
        )

    def test_start_date_field_type(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertIsInstance(reservation.start_date, date)

    def test_end_date_field(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertEqual(
            reservation.end_date.strftime("%Y-%m-%d %H:%M:%S"), "2024-01-01 11:00:00"
        )

    def test_end_date_field_type(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertIsInstance(reservation.end_date, date)

    def test_note_field(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        self.assertEqual(reservation.note, "Test note")

    def test_note_blank_null(self):
        reservation = Reservation.objects.get(id=self.reservation2.id)
        self.assertIsNone(reservation.note)

    def test_str_representation(self):
        reservation = Reservation.objects.get(id=self.reservation.id)
        expected_str = "Reservation for Test Team on 2024-01-01 at 10:00:00 by John Doe"
        self.assertEqual(str(reservation), expected_str)


class CommentModelTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.user = get_user_model().objects.create_user(
            username="TestUser",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="123456789",
            team=None,
        )
        self.room = Room.objects.create(
            name="Test Room", capacity=5, description="Test room", is_active=True
        )
        self.comment = Comment.objects.create(
            content="Test comment", user=self.user, room=self.room
        )

    def test_content_field(self):
        comment = Comment.objects.get(id=self.comment.id)
        self.assertEqual(comment.content, "Test comment")

    def test_created_at_field(self):
        comment = Comment.objects.get(id=self.comment.id)
        self.assertIsNotNone(comment.created_at)

    def test_user_field(self):
        comment = Comment.objects.get(id=self.comment.id)
        self.assertEqual(comment.user, self.user)

    def test_room_field(self):
        comment = Comment.objects.get(id=self.comment.id)
        self.assertEqual(comment.room, self.room)


class RatingModelTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.user = get_user_model().objects.create_user(
            username="TestUser",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="123456789",
            team=None,
        )
        self.room = Room.objects.create(
            name="Test Room", capacity=5, description="Test room", is_active=True
        )

    def test_rating_model(self):
        rating = Rating.objects.create(value=5, user=self.user, room=self.room)
        self.assertEqual(rating.value, 5)
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.room, self.room)

    def test_unique_rating_constraint(self):
        Rating.objects.create(value=3, user=self.user, room=self.room)
        with self.assertRaises(Exception):
            Rating.objects.create(value=4, user=self.user, room=self.room)

    def test_rating_value_validation(self):
        # Test valid rating value
        rating = Rating(value=3, user=self.user, room=self.room)
        rating.full_clean()

        # Test invalid rating value (less than 1)
        with self.assertRaises(ValidationError):
            Rating(value=0, user=self.user, room=self.room).full_clean()

        # Test invalid rating value (greater than 5)
        with self.assertRaises(ValidationError):
            Rating(value=6, user=self.user, room=self.room).full_clean()
