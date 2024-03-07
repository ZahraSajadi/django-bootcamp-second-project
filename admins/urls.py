from django.urls import path
from .views import (
    AdminHomeView,
    AdminReservationDeleteView,
    AdminReservationDetailView,
    AdminReservationListView,
    AdminRoomCreateView,
    AdminRoomDeleteView,
    AdminRoomDetailView,
    AdminRoomListView,
    AdminRoomUpdateView,
    AdminTeamCreateView,
    AdminTeamDeleteView,
    AdminTeamDetailView,
    AdminTeamListView,
    AdminTeamUpdateView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserUpdateView,
)

app_name = "admins"

urlpatterns = [
    path("home", AdminHomeView.as_view(), name="home"),
    path("rooms/", AdminRoomListView.as_view(), name="room_list"),
    path("rooms/create", AdminRoomCreateView.as_view(), name="room_create"),
    path("rooms/<int:pk>", AdminRoomDetailView.as_view(), name="room_detail"),
    path("rooms/<int:pk>/update", AdminRoomUpdateView.as_view(), name="room_update"),
    path("rooms/<int:pk>/delete", AdminRoomDeleteView.as_view(), name="room_delete"),
    path("teams/", AdminTeamListView.as_view(), name="team_list"),
    path("teams/create", AdminTeamCreateView.as_view(), name="team_create"),
    path("teams/<int:pk>", AdminTeamDetailView.as_view(), name="team_detail"),
    path("teams/<int:pk>/update", AdminTeamUpdateView.as_view(), name="team_update"),
    path("teams/<int:pk>/delete", AdminTeamDeleteView.as_view(), name="team_delete"),
    path("reservations/", AdminReservationListView.as_view(), name="reservation_list"),
    path(
        "reservations/<int:pk>",
        AdminReservationDetailView.as_view(),
        name="reservation_detail",
    ),
    path(
        "reservations/<int:pk>/delete",
        AdminReservationDeleteView.as_view(),
        name="reservation_delete",
    ),
    path("users/", AdminUserListView.as_view(), name="user_list"),
    path("users/<int:pk>", AdminUserDetailView.as_view(), name="user_detail"),
    path("users/<int:pk>/update", AdminUserUpdateView.as_view(), name="user_update"),
]
