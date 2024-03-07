from django.urls import path
from django.contrib.auth.views import LoginView

from .views import (
    AdminTeamCreateView,
    AdminTeamDeleteView,
    AdminTeamDetailView,
    AdminTeamListView,
    AdminTeamUpdateView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserUpdateView,
    ProfileView,
    ProfileUpdateView,
    CustomPasswordChangeView,
)

app_name = "users"

urlpatterns = [
    # login is not implemented... just for run profile tests
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path(
        "profile/change-password/",
        CustomPasswordChangeView.as_view(),
        name="change_password",
    ),
    path("team/list", AdminTeamListView.as_view(), name="team_list"),
    path("team/create", AdminTeamCreateView.as_view(), name="team_create"),
    path("team/<int:pk>", AdminTeamDetailView.as_view(), name="team_detail"),
    path("team/<int:pk>/update", AdminTeamUpdateView.as_view(), name="team_update"),
    path("team/<int:pk>/delete", AdminTeamDeleteView.as_view(), name="team_delete"),
    path("list/", AdminUserListView.as_view(), name="user_list"),
    path("<int:pk>", AdminUserDetailView.as_view(), name="user_detail"),
    path("<int:pk>/update", AdminUserUpdateView.as_view(), name="user_update"),
]
