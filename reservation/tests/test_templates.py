from datetime import datetime, timedelta
from warnings import filterwarnings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from reservation.models import Rating, Reservation, Room, Comment
from second_project.settings import TEAM_LEADERS_GROUP_NAME
from users.models import Team

filterwarnings("ignore", category=RuntimeWarning)
User = get_user_model()


class RoomDetailViewTest(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.user = User.objects.create_user(
            username="superuser",
            password="password",
            first_name="hossein",
            last_name="hosseini",
            email="test@noemail.invalid",
            phone="09123456789",
        )
        self.room = Room.objects.create(name="Test Room", capacity=5, description="Test description", is_active=True)
        self.comment = Comment.objects.create(room=self.room, content="First Comment", user=self.user)
        self.rate = Rating.objects.create(user=self.user, room=self.room, value=5)

    def test_room_detail_template_unauthenticated_user(self):
        url = reverse("reservation:room_detail", kwargs={"pk": self.room.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room.name)
        self.assertContains(response, f"Capacity: {self.room.capacity}")
        self.assertContains(response, f"Description: {self.room.description}")
        self.assertContains(response, "Status: Available")
        self.assertNotContains(response, "Status: Not Available")
        self.assertContains(response, f"Rating: {self.rate.value}")
        self.assertContains(
            response,
            f'{self.comment.content} - {self.comment.user} - {self.comment.created_at.strftime("%-B %-d, %-Y, %-I:%M")}',
        )
        self.assertNotContains(response, "Submit Rating")
        self.assertNotContains(response, "Add a Comment")

    def test_room_detail_template_authenticated_user(self):
        self.client.login(username=self.user.username, password="password")
        url = reverse("reservation:room_detail", kwargs={"pk": self.room.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room.name)
        self.assertContains(response, f"Capacity: {self.room.capacity}")
        self.assertContains(response, f"Description: {self.room.description}")
        self.assertContains(response, "Status: Available")
        self.assertNotContains(response, "Status: Not Available")
        self.assertContains(response, f"Rating: {self.rate.value}")
        self.assertContains(
            response,
            f'{self.comment.content} - {self.comment.user} - {self.comment.created_at.strftime("%-B %-d, %-Y, %-I:%M")}',
        )
        self.assertContains(response, "Submit Rating")
        self.assertContains(response, "Add a Comment")

    def test_authenticated_user_can_submit_rating(self):
        self.client.login(username=self.user.username, password="password")
        url = reverse("reservation:submit_rating", kwargs={"room_id": self.room.id})
        response = self.client.post(url, {"value": 4})
        self.assertEqual(response.status_code, 302)
        rate = Rating.objects.filter(user=self.user, room=self.room).first()
        self.assertEqual(4, rate.value)

    def test_unauthenticated_user_cannot_submit_rating(self):
        url = reverse("reservation:submit_rating", kwargs={"room_id": self.room.id})
        response = self.client.post(url, {"value": 3})
        self.assertEqual(response.status_code, 302)
        rate = Rating.objects.filter(user=self.user, room=self.room).first()
        self.assertEqual(self.rate.value, rate.value)

    def test_authenticated_user_can_submit_comment(self):
        comment_content = "Test comment"
        self.client.login(username=self.user.username, password="password")
        url = reverse("reservation:submit_comment", kwargs={"room_id": self.room.id})
        response = self.client.post(url, {"content": comment_content})
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.filter(user=self.user, room=self.room).order_by("-created_at").first()
        self.assertEqual(comment_content, comment.content)

    def test_unauthenticated_user_cannot_submit_comment(self):
        comment_content = "Test comment"
        url = reverse("reservation:submit_comment", kwargs={"room_id": self.room.id})
        response = self.client.post(url, {"content": comment_content})
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.filter(user=self.user, room=self.room).order_by("-created_at").first()
        self.assertNotEqual(comment_content, comment.content)


class ReservationDeleteTemplateTestCase(TestCase):
    def setUp(self):
        call_command("create_groups_and_permissions")
        self.user = User.objects.create_user(username="user", password="password")
        self.admin = User.objects.create_user(
            username="admin",
            password="password",
            email="empty",
            phone="empty",
        )
        self.team_leaders_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
        self.team_leaders_group.user_set.add(self.user)
        self.admin.is_staff = True
        self.admin.save()
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
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())
        self.client.post(reverse("reservation:reservation_delete", kwargs={"pk": self.reservation.id}))
        self.assertFalse(Reservation.objects.filter(id=self.reservation.id).exists())

    def test_reservation_delete_team_leader(self):
        self.client.login(
            username=self.user.username,
            password="password",
        )
        self.user.team = self.team
        self.user.save()
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())
        self.client.post(reverse("reservation:reservation_delete", kwargs={"pk": self.reservation.id}))
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
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())
        response = self.client.post(reverse("reservation:reservation_delete", kwargs={"pk": self.reservation.id}))
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())
        self.assertEqual(response.status_code, 403)


class IndexTemplateTestCase(TestCase):
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

    def test_index_no_login(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 302)

    def test_index_normal_user(self):
        self.user.team = self.team1
        self.user.save()
        self.client.login(username=self.user.username, password="password")
        response = self.client.get("")
        self.assertContains(response, self.reservation1)
        self.assertNotContains(response, self.reservation2)
        self.assertNotContains(response, "Delete")
        self.assertNotContains(response, "Team Management")
        self.assertNotContains(response, "User Management")
        self.assertNotContains(response, "Room Management")

    def test_index_admin_user(self):
        self.user.team = self.team1
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.user.username, password="password")
        response = self.client.get("")
        self.assertContains(response, self.reservation1)
        self.assertNotContains(response, self.reservation2)
        self.assertContains(response, "Delete")
        self.assertContains(response, "Team Management")
        self.assertContains(response, "User Management")
        self.assertContains(response, "Room Management")

    def test_index_team_leader(self):
        self.user.team = self.team1
        self.team_leaders_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
        self.team_leaders_group.user_set.add(self.user)
        self.user.save()
        self.client.login(username=self.user.username, password="password")
        response = self.client.get("")
        self.assertContains(response, self.reservation1)
        self.assertNotContains(response, self.reservation2)
        self.assertContains(response, "Delete")
        self.assertNotContains(response, "Team Management")
        self.assertNotContains(response, "User Management")
        self.assertNotContains(response, "Room Management")


class RoomManagementTemplateTestCase(TestCase):
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
        self.room = Room.objects.create(name="Test Room", capacity=10)

    def test_room_list_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("reservation:room_list"))
        self.assertEqual(response.status_code, 403)

    def test_room_create_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("reservation:room_create"))
        self.assertEqual(response.status_code, 403)

    def test_room_update_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("reservation:room_update", kwargs={"pk": self.room.id}))
        self.assertEqual(response.status_code, 403)

    def test_room_delete_normal_user(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse("reservation:room_delete", kwargs={"pk": self.room.id}))
        self.assertEqual(response.status_code, 403)

    def test_room_list_template(self):
        self.client.login(username=self.admin.username, password="password")
        response = self.client.get(reverse("reservation:room_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room)
        self.assertTemplateUsed(response, "reservation/room_list.html")

    def test_room_create_template(self):
        self.client.login(username=self.admin.username, password="password")
        response = self.client.get(reverse("reservation:room_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reservation/room_create.html")

    def test_room_update_template(self):
        self.client.login(username=self.admin.username, password="password")
        response = self.client.get(reverse("reservation:room_update", args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room)
        self.assertTemplateUsed(response, "reservation/room_update.html")

    def test_room_create(self):
        self.client.login(username=self.admin.username, password="password")
        room_name = "New Room"
        data = {"name": room_name, "capacity": 50, "is_active": "on", "description": "1"}
        response = self.client.post(reverse("reservation:room_create"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Room.objects.filter(name=room_name).exists())

    def test_room_update(self):
        self.client.login(username=self.admin.username, password="password")
        new_room_name = "New Room Name"
        data = {"name": new_room_name, "capacity": 50, "is_active": "on", "description": "1"}
        response = self.client.post(reverse("reservation:room_update", kwargs={"pk": self.room.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Room.objects.filter(name=new_room_name).exists())
        self.assertFalse(Room.objects.filter(name=self.room.name).exists())

    def test_room_delete(self):
        self.client.login(username=self.admin.username, password="password")
        self.assertTrue(Room.objects.filter(name=self.room.name).exists())
        response = self.client.post(reverse("reservation:room_delete", kwargs={"pk": self.room.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Room.objects.filter(name=self.room.name).exists())
