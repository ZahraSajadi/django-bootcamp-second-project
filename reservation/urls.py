from django.urls import path
from .views import (
    ReservationDeleteView,
    ReservationDetailView,
    ReservationListView,
    RoomCreateView,
    RoomDeleteView,
    RoomListView,
    RoomUpdateView,
    CommentSubmissionView,
    RatingSubmissionView,
    RoomDetail,
)

app_name = "reservation"

urlpatterns = [
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
    path("room/create", RoomCreateView.as_view(), name="room_create"),
    path("room/list", RoomListView.as_view(), name="room_list"),
    path("room/<int:pk>", RoomDetail.as_view(), name="room_detail"),
    path("room/<int:pk>/update", RoomUpdateView.as_view(), name="room_update"),
    path("room/<int:pk>/delete", RoomDeleteView.as_view(), name="room_delete"),
    path("list/", ReservationListView.as_view(), name="reservation_list"),
    path(
        "<int:pk>",
        ReservationDetailView.as_view(),
        name="reservation_detail",
    ),
    path(
        "<int:pk>/delete",
        ReservationDeleteView.as_view(),
        name="reservation_delete",
    ),
]
