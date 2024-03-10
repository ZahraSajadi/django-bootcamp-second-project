from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import get_user_model, login
from .models import Team
from .forms import (
    CustomPasswordChangeForm,
    EnterOTPForm,
    ProfileUpdateForm,
    RequestOTPForm,
    TeamCreateUpdateForm,
    UserCreateForm,
    UserUpdateForm,
)
from .mixins import UserNotAuthenticatedMixin

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


class UserCreate(UserNotAuthenticatedMixin, CreateView):
    form_class = UserCreateForm
    template_name = "users/signup.html"
    success_url = reverse_lazy("users:login_with_username")


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
    template_name = "shared/confirm_delete.html"


# class PhoneLoginView(View):
#     template_name = "users/login.html"
#     form_class = PhoneLoginForm

#     def get(self, request):
#         form = self.form_class()
#         return render(request, self.template_name, {"form": form})

#     def post(self, request):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             phone = form.cleaned_data["phone"]
#             user = User.objects.filter(phone=phone).first()

#             if user:
#                 otp_code = generate_otp()
#                 OTP.objects.create(user=user, otp=otp_code)
#                 print(f"OTP for {user.phone}: {otp_code}")
#                 messages.success(request, "OTP has been sent to your phone.")
#                 return redirect("profile")
#             else:
#                 messages.error(request, "User with this phone number does not exist.")
#         return render(request, self.template_name, {"form": form})


class RequestOTPView(UserNotAuthenticatedMixin, View):
    template_name = "users/login.html"
    form_class = RequestOTPForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        context = {}
        context["email"] = request.POST.get("email", None)
        context["phone"] = request.POST.get("phone", None)
        if form.is_valid():
            otp = form.save()
            if context["email"]:
                send_mail(
                    "OTP Code for unChained",
                    message=f"Your otp code is: {otp.otp}",
                    from_email="noreply@unchained.com",
                    recipient_list=(otp.user.email,),
                )
            if context["phone"]:
                print(f"SMS Sent\nYour otp code is: {otp.otp}")
            redirect_url = reverse("users:otp") + f"?email={context.get('email', '')}&phone={context.get('phone', '')}"
            return redirect(redirect_url)
        context["form"] = form
        return render(request, self.template_name, context)


class EnterOTPView(UserNotAuthenticatedMixin, View):
    template_name = "users/login.html"
    form_class = EnterOTPForm

    def get(self, request):
        context = {}
        context["email"] = request.GET.get("email", "")
        context["phone"] = request.GET.get("phone", "")
        form = self.form_class(user_info=context)
        context["form"] = form
        return render(request, self.template_name, context)

    def post(self, request):
        email = request.POST.get("email", "")
        phone = request.POST.get("phone", "")
        user_info = {}
        if email:
            user_info["email"] = email
        if phone:
            user_info["phone"] = phone
        form = self.form_class(request.POST, user_info=user_info)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            return redirect("index")
        user_info["form"] = form
        return render(request, self.template_name, user_info)


# class UsernameLoginView(View):
#     template_name = "users/login_with_username.html"
#     form_class = AuthenticationForm

#     def get(self, request, *args, **kwargs):
#         form = self.form_class(request, data=request.POST or None)
#         return render(request, self.template_name, {"form": form})

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get("username")
#             password = form.cleaned_data.get("password")
#             user = authenticate(request, username=username, password=password)

#             if user is not None:
#                 login(request, user)
#                 messages.success(request, "You are now logged in.")
#                 return redirect("profile")
#             else:
#                 messages.error(request, "Invalid username or password.")
#         return render(request, self.template_name, {"form": form})
