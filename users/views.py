from django.urls import reverse
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import get_user_model


class ProfileView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = "profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    fields = ["username", "first_name", "last_name", "email", "phone", "profile_image"]
    template_name = "profile_update.html"
    success_url = reverse("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "change_password.html"
    success_url = reverse("users:profile")
