from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import UserCreateForm


class UserCreate(CreateView):
    form_class = UserCreateForm
    template_name = 'user/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.user.team = None
        return super().form_valid(form)
# Create your views here.
