from django.contrib.auth.mixins import UserPassesTestMixin


class UserNotAuthenticatedMixin(UserPassesTestMixin):
    def test_func(self) -> bool | None:
        if self.request.user.is_authenticated:
            return False
        return True
