from django.urls import path
from django.contrib.auth.views import LoginView

from .views import ProfileView, ProfileUpdateView, CustomPasswordChangeView

app_name = "users"

urlpatterns = [
    # login is not implemented... just for run profile tests
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path(
        "profile/change-password/",
        CustomPasswordChangeView.as_view(),
        name="change_password",
    ),
]
