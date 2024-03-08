from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import get_user_model
from .models import Team
from .forms import TeamCreateUpdateForm

User = get_user_model()


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user

    def get_login_url(self):
        return reverse("users:login")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
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


class UserListView(PermissionRequiredMixin, ListView): ...


class UserDetailView(PermissionRequiredMixin, DetailView): ...


class UserUpdateView(PermissionRequiredMixin, UpdateView): ...


class TeamListView(PermissionRequiredMixin, ListView):
    permission_required = "users.view_team"
    model = Team
    ordering = ["id"]


class TeamCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "users.add_team"
    model = Team
    form_class = TeamCreateUpdateForm
    template_name = "users/team_create.html"
    success_url = reverse_lazy("users:team_list")


class TeamUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ["users.change_team", "users.view_team"]
    model = Team
    form_class = TeamCreateUpdateForm
    template_name = "users/team_update.html"
    success_url = reverse_lazy("users:team_list")


class TeamDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_team"
    model = Team
    success_url = reverse_lazy("users:team_list")
