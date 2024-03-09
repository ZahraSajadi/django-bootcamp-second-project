from django.urls import path

from users.views import UserCreate

app_name = "users"

urlpatterns = [
    path('sign-up', UserCreate.as_view(), name='sign_up'),
]
