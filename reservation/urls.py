from django.urls import path
from .views import CommentSubmissionView, RatingSubmissionView, RoomDetail

app_name = "reservation"

urlpatterns = [
    path("detail/<int:pk>", RoomDetail.as_view(), name="room_detail"),
    path(
        "submit_rating/<int:room_id>",
        RatingSubmissionView.as_view(),
        name="submit_rating",
    ),
    path(
        "submit_comment/<int:room_id>",
        CommentSubmissionView.as_view(),
        name="submit_comment",
    ),
]
