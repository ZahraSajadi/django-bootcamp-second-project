from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls import reverse
from reservation.models import Room, Comment
from reservation.views import RoomDetail, RatingSubmissionView, CommentSubmissionView

User = get_user_model()


class RoomDetailViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.room = Room.objects.create(
            name="Test Room", capacity=5, description="Test description", is_active=True
        )
        self.user = User.objects.create_user(
            username="superuser",
            password="password",
            first_name="hossein",
            last_name="hosseini",
            email="test@noemail.invalid",
            phone="09123456789",
        )
        self.comment = Comment.objects.create(
            room=self.room, content="Test comment", user=self.user
        )

    def test_room_detail_view(self):
        request = self.factory.get(
            reverse("reservation:room_detail", kwargs={"pk": self.room.id})
        )
        request.user = AnonymousUser()
        response = RoomDetail.as_view()(request, pk=self.room.id)
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

    def test_authenticated_user_can_submit_comment(self):
        self.client.login(username=self.user.username, password="password")
        request = self.factory.post(
            reverse("reservation:submit_comment", kwargs={"room_id": self.room.id}),
            {"content": "Test comment"},
        )
        request.user = self.user
        request.session = self.client.session
        response = CommentSubmissionView.as_view()(request, room_id=self.room.id)
        self.assertEqual(response.status_code, 302)
