from django.shortcuts import render
from django import http
from .forms import LoginForm


def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "index.html", {"form": form})
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
        return render(request, "test.html", {"phone": phone})
    else:
        raise http.HttpResponseBadRequest()
