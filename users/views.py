from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib import messages
from utils.db.model_helper import generate_otp
from .models import OTP, Team
from .forms import (
    CustomPasswordChangeForm,
    PhoneLoginForm,
    ProfileUpdateForm,
    TeamCreateUpdateForm,
    UserCreateForm,
    UserUpdateForm,
)

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


class PhoneLoginView(View):
    template_name = "users/login.html"
    form_class = PhoneLoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
            user = User.objects.filter(phone=phone).first()

            if user:
                otp_code = generate_otp()
                OTP.objects.create(user=user, otp=otp_code)
                print(f"OTP for {user.phone}: {otp_code}")
                messages.success(request, "OTP has been sent to your phone.")
                return redirect("profile")
            else:
                messages.error(request, "User with this phone number does not exist.")
        return render(request, self.template_name, {"form": form})


class UsernameLoginView(View):
    template_name = "users/login_with_username.html"
    form_class = AuthenticationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(request, data=request.POST or None)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "You are now logged in.")
                return redirect("profile")
            else:
                messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {"form": form})
