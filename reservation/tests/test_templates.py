from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from reservation.models import Rating, Room, Comment

User = get_user_model()


class RoomDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="superuser",
            password="password",
            first_name="hossein",
            last_name="hosseini",
            email="test@noemail.invalid",
            phone="09123456789",
        )
        self.room = Room.objects.create(
            name="Test Room", capacity=5, description="Test description", is_active=True
        )
        self.comment = Comment.objects.create(
            room=self.room, content="First Comment", user=self.user
        )
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
            f'{self.comment.content} - {self.comment.user} - {self.comment.created_at.strftime("%-B %-d, %-Y, %-I:%-M")}',
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
            f'{self.comment.content} - {self.comment.user} - {self.comment.created_at.strftime("%-B %-d, %-Y, %-I:%-M")}',
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
        comment = (
            Comment.objects.filter(user=self.user, room=self.room)
            .order_by("-created_at")
            .first()
        )
        self.assertEqual(comment_content, comment.content)

    def test_unauthenticated_user_cannot_submit_comment(self):
        comment_content = "Test comment"
        url = reverse("reservation:submit_comment", kwargs={"room_id": self.room.id})
        response = self.client.post(url, {"content": comment_content})
        self.assertEqual(response.status_code, 302)
        comment = (
            Comment.objects.filter(user=self.user, room=self.room)
            .order_by("-created_at")
            .first()
        )
        self.assertNotEqual(comment_content, comment.content)
