from django.urls import reverse
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
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

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("users:profile")

    def form_valid(self, form):
        user = form.save(commit=False)
        new_image = self.request.FILES.get("profile_image")
        if new_image:
            print("zico", new_image)
        else:
            user.profile_image = None
        user.save(
            update_fields=[
                "username",
            ]
        )
        return super().form_valid(form)


# class PasswordUpdateView(LoginRequiredMixin, UpdateView):
#     template_name = 'change_password.html'
#     form_class = ChangePasswordForm
#     success_url = reverse('users:profile')
