from django.urls import path
from .views import ProfileView, ProfileUpdateView, CustomPasswordChangeView

app_name = "users"

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path(
        "profile/change-password/",
        CustomPasswordChangeView.as_view(),
        name="change_password",
    ),
]
