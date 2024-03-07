from django.urls import path
from .views import (
    AdminHome,
    AdminReservationDetail,
    AdminReservationList,
    AdminRoomDetail,
    AdminRoomList,
    AdminTeamDetail,
    AdminTeamList,
    AdminUserDetail,
    AdminUserList,
)

app_name = "admins"

urlpatterns = [
    path("home", AdminHome.as_view(), name="home"),
    path("rooms/", AdminRoomList.as_view(), name="room_list"),
    path("rooms/<int:pk>", AdminRoomDetail.as_view(), name="room_detail"),
    path("teams/", AdminTeamList.as_view(), name="team_list"),
    path("teams/<int:pk>", AdminTeamDetail.as_view(), name="team_detail"),
    path("reservations/", AdminReservationList.as_view(), name="reservation_list"),
    path(
        "reservations/<int:pk>",
        AdminReservationDetail.as_view(),
        name="reservation_detail",
    ),
    path("users/", AdminUserList.as_view(), name="user_list"),
    path("users/<int:pk>", AdminUserDetail.as_view(), name="user_detail"),
]
