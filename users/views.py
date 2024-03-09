from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

from users.forms import PhoneLoginForm
from users.models import OTP, CustomUser
from utils.db.model_helper import generate_otp
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
            user = CustomUser.objects.filter(phone=phone).first()

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
