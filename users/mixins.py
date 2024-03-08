from django.contrib.auth.mixins import PermissionRequiredMixin


class CustomPermReqMixin(PermissionRequiredMixin):
    login_url = "users:login"
