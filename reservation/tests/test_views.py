from datetime import datetime
from warnings import filterwarnings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.timezone import timedelta
from reservation.models import Reservation, Room, Comment, Rating
from users.models import Team
from reservation.views import (
    ReservationDeleteView,
    RoomDetailView,
    RatingSubmissionView,
    CommentSubmissionView,
    UserReservationListView,
)
from second_project.settings import TEAM_LEADERS_GROUP_NAME

filterwarnings("ignore", category=RuntimeWarning)
User = get_user_model()


class RoomDetailViewTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.factory = RequestFactory()
        self.room = Room.objects.create(name="Test Room", capacity=5, description="Test description", is_active=True)
        self.user = User.objects.create_user(
            username="superuser",
            password="password",
            first_name="hossein",
            last_name="hosseini",
            email="test@noemail.invalid",
            phone="09123456789",
        )
        self.comment = Comment.objects.create(room=self.room, content="First comment", user=self.user)

    def test_room_detail_view(self):
        request = self.factory.get(reverse("reservation:room_detail", kwargs={"pk": self.room.id}))
        request.user = AnonymousUser()
        response = RoomDetailView.as_view()(request, pk=self.room.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room.name)
        self.assertContains(response, f"Capacity: {self.room.capacity}")
        self.assertContains(response, f"Description: {self.room.description}")
        self.assertContains(response, "Status: Available")
        self.assertNotContains(response, "Status: Not Available")
        self.assertContains(response, "Rating: 0")
        self.assertContains(
            response,
            f"{self.comment.content} - {self.comment.user} - {self.comment.created_at.strftime('%-B %-d, %-Y, %-I:%M')}",
        )

    def test_authenticated_user_can_submit_rating(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.post(
            reverse("reservation:submit_rating", kwargs={"room_id": self.room.id}),
            {"value": 5},
        )
        request.user = self.user
        request.session = self.client.session
        response = RatingSubmissionView.as_view()(request, room_id=self.room.id)
        self.assertEqual(response.status_code, 302)
        rate = Rating.objects.filter(user=self.user, room=self.room).first()
        self.assertEqual(5, rate.value)

    def test_authenticated_user_can_submit_comment(self):
        comment_content = "Test comment"
        self.client.login(username=self.user.username, password="password")
        request = self.factory.post(
            reverse("reservation:submit_comment", kwargs={"room_id": self.room.id}),
            {"content": comment_content},
        )
        request.user = self.user
        request.session = self.client.session
        response = CommentSubmissionView.as_view()(request, room_id=self.room.id)
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.filter(user=self.user, room=self.room).order_by("-created_at").first()
        self.assertEqual(comment_content, comment.content)


class ReservationDeleteViewTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="user", password="password")
        self.admin = User.objects.create_user(
            username="admin",
            password="password",
            email="empty",
            phone="empty",
        )
        self.team_leaders_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
        self.admin.is_staff = True
        self.admin.save()
        self.team_leaders_group.user_set.add(self.user)
        self.team = Team.objects.create(name="Team")
        self.room = Room.objects.create(name="Room", capacity=10)
        self.reservation = Reservation.objects.create(
            team=self.team,
            room=self.room,
            start_date=datetime.now(),
            end_date=datetime.now(),
        )

    def test_reservation_delete_admin(self):
        self.client.login(
            username=self.admin.username,
            password="password",
        )
        request = self.factory.post(
            reverse("reservation:reservation_delete", kwargs={"pk": self.reservation.id}),
        )
        request.user = self.admin
        request.session = self.client.session
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())
        ReservationDeleteView.as_view()(request, pk=self.reservation.id)
        self.assertFalse(Reservation.objects.filter(id=self.reservation.id).exists())

    def test_reservation_delete_team_leader(self):
        self.client.login(
            username=self.user.username,
            password="password",
        )
        self.user.team = self.team
        self.user.save()
        request = self.factory.post(
            reverse("reservation:reservation_delete", kwargs={"pk": self.reservation.id}),
        )
        request.user = self.user
        request.session = self.client.session
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())
        ReservationDeleteView.as_view()(request, pk=self.reservation.id)
        self.assertFalse(Reservation.objects.filter(id=self.reservation.id).exists())

    def test_reservation_delete_normal_member(self):
        normal_member = User.objects.create_user(
            username="normal",
            password="password",
            email="empty1",
            phone="empty1",
        )
        self.client.login(
            username=normal_member.username,
            password="password",
        )
        normal_member.team = self.team
        normal_member.save()
        request = self.factory.post(
            reverse("reservation:reservation_delete", kwargs={"pk": self.reservation.id}),
        )
        request.user = normal_member
        request.session = self.client.session
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())
        with self.assertRaises(PermissionDenied):
            ReservationDeleteView.as_view()(request, pk=self.reservation.id)


class UserReservationListViewTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="user", password="password")
        self.admin = User.objects.create_user(
            username="admin",
            password="password",
            email="empty",
            phone="empty",
        )
        self.admin.is_staff = True
        self.admin.save()
        self.team1 = Team.objects.create(name="Team One")
        self.team2 = Team.objects.create(name="Team Two")
        self.room = Room.objects.create(name="Room", capacity=10)
        self.reservation1 = Reservation.objects.create(
            team=self.team1,
            room=self.room,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=1),
        )
        self.reservation2 = Reservation.objects.create(
            team=self.team2,
            room=self.room,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=1),
        )
        self.user.team = self.team1
        self.user.save()

    def test_index_no_login(self):
        request = self.factory.get("")
        request.user = AnonymousUser
        response = UserReservationListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.reservation1)

    def test_index_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get("")
        request.user = self.user
        request.session = self.client.session
        response = UserReservationListView.as_view()(request)
        self.assertContains(response, self.reservation1)
        self.assertNotContains(response, self.reservation2)
        self.assertNotContains(response, "Delete")

    def test_index_admin_user(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get("")
        request.user = self.user
        request.session = self.client.session
        response = UserReservationListView.as_view()(request)
        self.assertContains(response, self.reservation1)
        self.assertNotContains(response, self.reservation2)
        self.assertContains(response, "Delete")

    def test_index_team_leader(self):
        self.team_leaders_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
        self.team_leaders_group.user_set.add(self.user)
        self.user.save()
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get("")
        request.user = self.user
        request.session = self.client.session
        response = UserReservationListView.as_view()(request)
        self.assertContains(response, self.reservation1)
        self.assertNotContains(response, self.reservation2)
        self.assertContains(response, "Delete")
