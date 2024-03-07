from django.urls import path
from .views import (
    AdminReservationDeleteView,
    AdminReservationDetailView,
    AdminReservationListView,
    AdminRoomCreateView,
    AdminRoomDeleteView,
    AdminRoomListView,
    AdminRoomUpdateView,
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
    path("room/create", AdminRoomCreateView.as_view(), name="room_create"),
    path("room/list", AdminRoomListView.as_view(), name="room_list"),
    path("room/<int:pk>", RoomDetail.as_view(), name="room_detail"),
    path("room/<int:pk>/update", AdminRoomUpdateView.as_view(), name="room_update"),
    path("room/<int:pk>/delete", AdminRoomDeleteView.as_view(), name="room_delete"),
    path("list/", AdminReservationListView.as_view(), name="reservation_list"),
    path(
        "<int:pk>",
        AdminReservationDetailView.as_view(),
        name="reservation_detail",
    ),
    path(
        "<int:pk>/delete",
        AdminReservationDeleteView.as_view(),
        name="reservation_delete",
    ),
]
