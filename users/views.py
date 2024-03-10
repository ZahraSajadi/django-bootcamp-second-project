from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import get_user_model
from .models import Team
from .forms import CustomPasswordChangeForm, ProfileUpdateForm, TeamCreateUpdateForm, UserCreateForm, UserUpdateForm

User = get_user_model()


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "users/profile_update.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class UserCreate(UserPassesTestMixin, CreateView):
    form_class = UserCreateForm
    template_name = "users/signup.html"
    success_url = reverse_lazy("users:login")

    def test_func(self) -> bool | None:
        if self.request.user.is_authenticated:
            return False
        return True


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/change_password.html"
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("users:profile")


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = "users.view_customuser"
    models = User
    queryset = User.objects.all()
    ordering = ["id"]
    template_name = "users/user_list.html"


class UserUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ["users.change_customuser", "users.view_customuser"]
    model = User
    form_class = UserUpdateForm
    template_name = "users/profile_update.html"
    success_url = reverse_lazy("users:user_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        affected_user = self.get_object()
        if not self.request.user.is_superuser or affected_user.is_superuser:
            del form.fields["is_staff"]
        return form

    def post(self, request, *args, **kwargs):
        affected_user = self.get_object()
        if not self.request.user.is_superuser or affected_user.is_superuser:
            if "is_staff" in request.POST:
                return JsonResponse({"error": "You are not authorized to modify this field"}, status=403)
        return super().post(request, *args, **kwargs)


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
