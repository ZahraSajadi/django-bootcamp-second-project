from datetime import datetime, timedelta
from warnings import filterwarnings
from django.contrib.auth import get_user_model
from django.test import TestCase
from reservation.models import Comment, Rating, Reservation, Room
from users.models import Team

filterwarnings("ignore", category=RuntimeWarning)
User = get_user_model()


class RoomAdminTest(TestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(
            username="superuser",
            password="password",
            first_name="test_name",
            last_name="test_name",
            email="test@noemail.invalid",
            phone="09123456789",
        )
        self.room_active = Room.objects.create(
            name="active_room", description="good room", capacity=10, is_active=True
        )
        self.room_deactive = Room.objects.create(
            name="deactive_room", description="bad room", capacity=20, is_active=False
        )

    def test_room_model_admin_list_display(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get("/admin/reservation/room/")
        self.assertContains(response, "name")
        self.assertContains(response, "capacity")
        self.assertContains(response, "is_active")

    def test_room_model_admin_search(self):
        self.client.login(username=self.super_user.username, password="password")

        response = self.client.get("/admin/reservation/room/?q=good")
        self.assertContains(response, self.room_active.name)
        self.assertNotContains(response, self.room_deactive.name)

    def test_room_model_admin_filter(self):
        self.client.login(username=self.super_user.username, password="password")
        filter_params = {"is_active": True}
        response = self.client.get("/admin/reservation/room/", data=filter_params)
        self.assertContains(response, self.room_active.name)
        self.assertNotContains(response, self.room_deactive.name)

    def test_room_model_fieldsets(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get(
            f"/admin/reservation/room/{self.room_active.id}/change/"
        )
        self.assertContains(response, "Name:")
        self.assertContains(response, "Capacity:")
        self.assertContains(response, "Description:")
        self.assertContains(response, "is_active")
        self.assertContains(response, "Comments")
        self.assertContains(response, "Content")
        self.assertContains(response, "Ratings")
        self.assertContains(response, "Value")


class ReservationAdminTest(TestCase):
    def setUp(self):
        self.team1 = Team.objects.create(name="one")
        self.team2 = Team.objects.create(name="two")
        self.super_user = User.objects.create_superuser(
            username="superuser",
            password="password",
            first_name="hossein",
            last_name="hosseini",
            email="test@noemail.invalid",
            phone="09123456789",
            team=self.team1,
        )
        self.user = User.objects.create_user(
            username="normaluser",
            password="password",
            first_name="amir",
            last_name="amiri",
            email="test@email.invalid",
            phone="09133456789",
            is_active=False,
            team=self.team2,
        )
        self.room1 = Room.objects.create(
            name="blue", description="good room", capacity=10, is_active=True
        )
        self.room2 = Room.objects.create(
            name="red", description="bad room", capacity=20, is_active=True
        )
        self.start1 = datetime.now()
        self.end1 = self.start1 + timedelta(hours=1)

        self.start2 = self.start1 + timedelta(days=1)
        self.end2 = self.start2 + timedelta(hours=1)

        self.reserv1 = Reservation.objects.create(
            room=self.room1,
            reserver_user=self.super_user,
            team=self.team1,
            start_date=self.start1,
            end_date=self.end1,
        )
        self.reserv2 = Reservation.objects.create(
            room=self.room2,
            reserver_user=self.user,
            team=self.team2,
            start_date=self.start2,
            end_date=self.end2,
        )

    def test_reservation_model_admin_list_display(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get("/admin/reservation/reservation/")
        self.assertContains(response, "room")
        self.assertContains(response, "reserver_user")
        self.assertContains(response, "team")
        self.assertContains(response, "start_date")
        self.assertContains(response, "end_date")

    def test_reservation_model_admin_filter(self):
        self.client.login(username=self.super_user.username, password="password")

        filter_params = {"room__id__exact": self.room1.id}
        response = self.client.get(
            "/admin/reservation/reservation/", data=filter_params
        )
        self.assertContains(response, self.reserv1)
        self.assertNotContains(response, self.reserv2)

        filter_params = {"reserver_user__id__exact": self.super_user.id}
        response = self.client.get(
            "/admin/reservation/reservation/", data=filter_params
        )
        self.assertContains(response, self.reserv1)
        self.assertNotContains(response, self.reserv2)

        filter_params = {"team__id__exact": self.team1.id}
        response = self.client.get(
            "/admin/reservation/reservation/", data=filter_params
        )
        self.assertContains(response, self.reserv1)
        self.assertNotContains(response, self.reserv2)

        filter_params = {"team__id__exact": self.team1.id}
        response = self.client.get(
            "/admin/reservation/reservation/", data=filter_params
        )
        self.assertContains(response, self.reserv1)
        self.assertNotContains(response, self.reserv2)

        filter_params = {"start_date": self.start1}
        response = self.client.get(
            "/admin/reservation/reservation/", data=filter_params
        )
        self.assertContains(response, self.reserv1)
        self.assertNotContains(response, self.reserv2)

        filter_params = {"end_date": self.end1}
        response = self.client.get(
            "/admin/reservation/reservation/", data=filter_params
        )
        self.assertContains(response, self.reserv1)
        self.assertNotContains(response, self.reserv2)

    def test_room_model_fieldsets(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get(
            f"/admin/reservation/reservation/{self.reserv1.id}/change/"
        )
        self.assertContains(response, "Room:")
        self.assertContains(response, "Reserver user:")
        self.assertContains(response, "Team:")
        self.assertContains(response, "Start date:")
        self.assertContains(response, "End date:")
        self.assertContains(response, "Note:")


class CommentAdminTest(TestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(
            username="superuser",
            password="password",
            first_name="hossein",
            last_name="hosseini",
            email="test@noemail.invalid",
            phone="09123456789",
        )
        self.user = User.objects.create_user(
            username="normaluser",
            password="password",
            first_name="amir",
            last_name="amiri",
            email="test@email.invalid",
            phone="09133456789",
            is_active=False,
        )
        self.room1 = Room.objects.create(
            name="blue", description="good room", capacity=10, is_active=True
        )
        self.room2 = Room.objects.create(
            name="red", description="bad room", capacity=20, is_active=True
        )
        self.date1 = datetime.now()
        self.date2 = self.date1 + timedelta(days=1)
        self.comment1 = Comment.objects.create(
            content="very good room",
            user=self.super_user,
            room=self.room1,
        )
        self.comment1.created_at = self.date1
        self.comment1.save()

        self.comment2 = Comment.objects.create(
            content="very bad room",
            user=self.user,
            room=self.room2,
        )
        self.comment2.created_at = self.date2
        self.comment2.save()

    def test_comment_model_admin_list_display(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get("/admin/reservation/comment/")
        self.assertContains(response, "user")
        self.assertContains(response, "room")
        self.assertContains(response, "created_at")
        self.assertContains(response, "short_content")

    def test_comment_model_admin_filter(self):
        self.client.login(username=self.super_user.username, password="password")

        filter_params = {"user__id__exact": self.super_user.id}
        response = self.client.get("/admin/reservation/comment/", data=filter_params)
        self.assertContains(response, self.comment1.content)
        self.assertNotContains(response, self.comment2.content)

        filter_params = {"room__id__exact": self.room1.id}
        response = self.client.get("/admin/reservation/comment/", data=filter_params)
        self.assertContains(response, self.comment1.content)
        self.assertNotContains(response, self.comment2.content)

        filter_params = {"created_at": self.date1}
        response = self.client.get("/admin/reservation/comment/", data=filter_params)
        self.assertContains(response, self.comment1.content)
        self.assertNotContains(response, self.comment2.content)

    def test_comment_model_search(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get("/admin/reservation/comment/?q=good")
        self.assertContains(response, self.comment1.content)
        self.assertNotContains(response, self.comment2.content)

    def test_comment_model_fieldtest(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get(
            f"/admin/reservation/comment/{self.comment1.id}/change/"
        )
        self.assertContains(response, "Content:")
        self.assertContains(response, "User:")
        self.assertContains(response, "Room:")


class RatingAdminTest(TestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(
            username="superuser",
            password="password",
            first_name="hossein",
            last_name="hosseini",
            email="test@noemail.invalid",
            phone="09123456789",
        )
        self.user = User.objects.create_user(
            username="normaluser",
            password="password",
            first_name="amir",
            last_name="amiri",
            email="test@email.invalid",
            phone="09133456789",
            is_active=False,
        )
        self.room1 = Room.objects.create(
            name="blue", description="good room", capacity=10, is_active=True
        )
        self.room2 = Room.objects.create(
            name="red", description="bad room", capacity=20, is_active=True
        )
        self.rate1 = Rating.objects.create(
            value=5, user=self.super_user, room=self.room1
        )
        self.rate2 = Rating.objects.create(value=4, user=self.user, room=self.room2)

    def test_rating_model_admin_list_display(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get("/admin/reservation/rating/")
        self.assertContains(response, "user")
        self.assertContains(response, "room")
        self.assertContains(response, "value")

    def test_rating_model_admin_filter(self):
        self.client.login(username=self.super_user.username, password="password")

        filter_params = {"user__id__exact": self.super_user.id}
        response = self.client.get("/admin/reservation/rating/", data=filter_params)
        self.assertContains(response, self.rate1)
        self.assertNotContains(response, self.rate2)

        filter_params = {"room__id__exact": self.room1.id}
        response = self.client.get("/admin/reservation/rating/", data=filter_params)
        self.assertContains(response, self.rate1)
        self.assertNotContains(response, self.rate2)

    def test_comment_model_fieldtest(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.client.get(f"/admin/reservation/rating/{self.rate1.id}/change/")
        self.assertContains(response, "Value:")
        self.assertContains(response, "User:")
        self.assertContains(response, "Room:")
