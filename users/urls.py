from django.urls import path
from django.contrib.auth.views import LoginView
from users.views import UserCreate
from .views import (
    TeamCreateView,
    TeamDeleteView,
    TeamListView,
    TeamUpdateView,
    UserListView,
    UserUpdateView,
    ProfileView,
    ProfileUpdateView,
    CustomPasswordChangeView,
)

app_name = "users"

urlpatterns = [
    # login is not implemented... just for run profile tests
    path("login/", LoginView.as_view(template_name="users/login.html", redirect_authenticated_user=True), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path(
        "profile/change-password/",
        CustomPasswordChangeView.as_view(),
        name="change_password",
    ),
    path("team/list", TeamListView.as_view(), name="team_list"),
    path("team/create", TeamCreateView.as_view(), name="team_create"),
    path("team/<int:pk>/update", TeamUpdateView.as_view(), name="team_update"),
    path("team/<int:pk>/delete", TeamDeleteView.as_view(), name="team_delete"),
    path("list/", UserListView.as_view(), name="user_list"),
    path("<int:pk>/update", UserUpdateView.as_view(), name="user_update"),
    path("sign-up", UserCreate.as_view(), name="sign_up"),
]
