from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import CustomUser
from .forms import SignUpForm

class SignUpView(CreateView):
    model = CustomUser
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')
