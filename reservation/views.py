from typing import Any
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.shortcuts import redirect
from django.views import View
from django.views.generic import DetailView
from .models import Comment, Room, Rating
from .forms import SubmitCommentForm, SubmitRatingForm


class RoomDetail(DetailView):
    model = Room
    template_name = "room_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        avg_rating = Rating.objects.filter(room=self.object).aggregate(
            avg_rate=Avg("value")
        )["avg_rate"]
        if not avg_rating:
            avg_rating = 0
        context["rate"] = avg_rating
        context["comments"] = Comment.objects.filter(room=self.object).all()
        context["room_id"] = self.kwargs.get("pk")
        user = self.request.user
        if not user.is_anonymous:
            rating = Rating.objects.filter(user=user).filter(room=self.object).first()
            context["rating_form"] = SubmitRatingForm(instance=rating)
            context["comment_form"] = SubmitCommentForm()
        return context


class RatingSubmissionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = get_user(request)
        room_id = kwargs.get("room_id")
        room = Room.objects.get(id=room_id)
        rate = Rating(user=user, room=room)
        rating_form = SubmitRatingForm(request.POST, instance=rate)
        if rating_form.is_valid():
            rating_form.save()
        return redirect("reservation:room_detail", pk=room_id)


class CommentSubmissionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = get_user(request)
        room_id = kwargs.get("room_id")
        room = Room.objects.get(id=room_id)
        comment = Comment(user=user, room=room)
        comment_form = SubmitCommentForm(request.POST, instance=comment)
        if comment_form.is_valid():
            comment_form.save()
        return redirect("reservation:room_detail", pk=room_id)
