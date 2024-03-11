from datetime import datetime
from warnings import filterwarnings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import JsonResponse
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.timezone import timedelta
from reservation.models import Reservation, Room, Comment, Rating
from users.models import Team
from reservation.views import (
    ReservationDeleteView,
    RoomCreateView,
    RoomDeleteView,
    RoomDetailView,
    RatingSubmissionView,
    CommentSubmissionView,
    RoomListView,
    RoomUpdateView,
    UserReservationListView,
    ReservationListView,
    ReservationListJson,
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


class ReservationListViewTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.factory = RequestFactory()
        self.team = Team.objects.create(name="Test Team")
        self.room = Room.objects.create(name="Test Room", capacity=10, is_active=True)
        Room.objects.create(name="Test Room2", capacity=10, is_active=False)

        self.user = User.objects.create_user(
            username="user", password="password", team=self.team, email="a@a.com", phone="empty1"
        )
        self.team_leader = User.objects.create_user(
            username="teamleader", password="password", team=self.team, email="b@b.com", phone="empty2"
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="password",
            email="admin@admin.com",
            phone="empty3",
        )
        self.team_leaders_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
        self.admin.is_staff = True
        self.admin.save()
        self.team_leaders_group.user_set.add(self.team_leader)

    def test_test_func_with_get_request(self):
        request = self.factory.get(reverse("reservation:reservation_list"))
        request.user = AnonymousUser
        view = ReservationListView()
        view.request = request
        self.assertTrue(view.test_func())

    def test_test_func_with_permission(self):
        request = self.factory.post(reverse("reservation:reservation_list"))
        request.user = self.admin
        view = ReservationListView()
        view.request = request
        self.assertTrue(view.test_func())

    def test_test_func_with_self_team_permission(self):
        request = self.factory.post(reverse("reservation:reservation_list"))
        request.user = self.team_leader
        request.POST = {"team": self.team.id}
        view = ReservationListView()
        view.request = request
        self.assertTrue(view.test_func())

    def test_test_func_without_permission(self):
        request = self.factory.post(reverse("reservation:reservation_list"))
        request.user = self.user
        view = ReservationListView()
        view.request = request
        self.assertFalse(view.test_func())

    def test_get_data(self):
        view = ReservationListView()
        data = view.get_data()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.room.id)
        self.assertEqual(data[0]["title"], self.room.name)

    def test_get_with_admin_permission(self):
        request = self.factory.get(reverse("reservation:reservation_list"))
        request.user = self.admin
        view = ReservationListView()
        view.request = request
        response = view.get(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_get_with_team_leader_permission(self):
        url = reverse("reservation:reservation_list")
        self.client.login(username="teamleader", password="password")

        request = self.factory.get(url)
        request.user = self.team_leader
        request.session = self.client.session

        view = ReservationListView()
        view.request = request
        response = view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_get_without_permission(self):
        request = self.factory.get(reverse("reservation:reservation_list"))
        request.user = AnonymousUser
        view = ReservationListView.as_view()
        view.request = request
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<form")

    def test_post_valid_form(self):
        data = {
            "room": self.room.id,
            "reserver_user": self.user.id,
            "team": self.team.id,
            "start_date": "2022-01-01 20:00:00",
            "end_date": "2022-01-02 21:00:00",
            "note": "Test reservation",
        }
        request = self.factory.post(reverse("reservation:reservation_list"), data)
        request.user = self.team_leader
        view = ReservationListView.as_view()
        view.request = request
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_post_invalid_form(self):
        request = self.factory.post(reverse("reservation:reservation_list"), {})
        request.user = self.team_leader
        view = ReservationListView()
        view.request = request
        response = view.post(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")


class ReservationListJsonTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="password", email="a@a.com", phone="empty1")
        self.reservation_date = self.today
        self.reservation = Reservation.objects.create(
            team_name="Test Team",
            room_name="Test Room",
            start_date="2024-3-10 9:00:00",
            end_date="2024-3-10 10:00:00",
            room_id=1,
            note="Test Note",
            reserver_user=self.user,
        )

    def test_get_method(self):
        # Create a mock request object
        request = self.client.get(reverse("reservation_list_json"), {"date": self.reservation_date})

        # Call the view function with the mock request
        response = ReservationListJson.as_view()(request)

        # Check if the response is a JsonResponse
        self.assertIsInstance(response, JsonResponse)

        # Check the content of the JsonResponse
        events = response.json()["events"]
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["id"], self.reservation.id)
        self.assertEqual(event["title"], self.reservation.team_name)
        self.assertEqual(event["room"], self.reservation.room_name)
        self.assertEqual(event["start"], self.reservation.start_date.isoformat())
        self.assertEqual(event["end"], self.reservation.end_date.isoformat())
        self.assertEqual(event["resourceId"], self.reservation.room_id)
        self.assertEqual(event["extendedProps"]["note"], self.reservation.note)
        self.assertEqual(event["extendedProps"]["reserver"], self.reservation.reserver_user.username)
        self.assertEqual(event["backgroundColor"], "green")
        self.assertEqual(event["borderColor"], "green")


class RoomManagementViewsTestCase(TestCase):
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
        self.room = Room.objects.create(name="Test Room", capacity=10)

    def test_room_list_view_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get(reverse("reservation:room_list"))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            RoomListView.as_view()(request)

    def test_room_create_view_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get(reverse("reservation:room_create"))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            RoomCreateView.as_view()(request)

    def test_room_update_view_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get(reverse("reservation:room_update", kwargs={"pk": self.room.id}))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            RoomUpdateView.as_view()(request)

    def test_room_delete_view_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.get(reverse("reservation:room_delete", kwargs={"pk": self.room.id}))
        request.user = self.user
        request.session = self.client.session
        with self.assertRaises(PermissionDenied):
            RoomDeleteView.as_view()(request)

    def test_room_list_view_admin_user(self):
        self.client.login(username=self.admin.username, password="password")
        request = self.factory.get(reverse("reservation:room_list"))
        request.user = self.admin
        request.session = self.client.session
        response = RoomListView.as_view()(request)
        self.assertContains(response, self.room)

    def test_room_create_view_admin_user(self):
        self.client.login(username=self.admin.username, password="password")
        room_name = "New room"
        data = {"name": room_name, "capacity": 50, "is_active": "on", "description": "1"}
        request = self.factory.post(reverse("reservation:room_create"), data)
        request.user = self.admin
        request.session = self.client.session
        response = RoomCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Room.objects.filter(name=room_name).exists())

    def test_room_update_view_admin_user(self):
        self.client.login(username=self.admin.username, password="password")
        room_name = "New room"
        data = {"name": room_name, "capacity": 50, "is_active": "on", "description": "1"}
        request = self.factory.post(reverse("reservation:room_update", kwargs={"pk": self.room.id}), data)
        request.user = self.admin
        request.session = self.client.session
        response = RoomUpdateView.as_view()(request, pk=self.room.id)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Room.objects.filter(name=room_name).exists())
        self.assertFalse(Room.objects.filter(name=self.room.name).exists())

    def test_room_delete_view_admin_user(self):
        self.client.login(username=self.admin.username, password="password")
        request = self.factory.post(reverse("reservation:room_delete", kwargs={"pk": self.room.id}))
        request.user = self.admin
        request.session = self.client.session
        response = RoomDeleteView.as_view()(request, pk=self.room.id)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Room.objects.filter(name=self.room.name).exists())
