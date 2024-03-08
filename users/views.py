from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import get_user_model
from .mixins import CustomPermReqMixin


class ProfileView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = "users/profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user

    def get_login_url(self):
        return reverse("users:login")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    fields = ["username", "first_name", "last_name", "email", "phone", "profile_image"]
    template_name = "users/profile_update.html"

    def get_success_url(self):
        return reverse("users:profile")

    def get_login_url(self):
        return reverse("users:login")

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/change_password.html"

    def get_success_url(self):
        return reverse("users:profile")

    def get_login_url(self):
        return reverse("users:login")


class UserListView(CustomPermReqMixin, ListView): ...


class UserDetailView(CustomPermReqMixin, DetailView): ...


class UserUpdateView(CustomPermReqMixin, UpdateView): ...


class TeamListView(CustomPermReqMixin, ListView): ...


class TeamDetailView(CustomPermReqMixin, DetailView): ...


class TeamCreateView(CustomPermReqMixin, CreateView): ...


class TeamUpdateView(CustomPermReqMixin, UpdateView): ...


class TeamDeleteView(CustomPermReqMixin, DeleteView): ...
