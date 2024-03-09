from typing import Any
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .models import Comment, Reservation, Room, Rating
from .forms import SubmitCommentForm, SubmitRatingForm


class RoomDetailView(DetailView):
    model = Room
    template_name = "reservation/room_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        avg_rating = self.object.get_avg_rating()
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


class UserReservationsView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "index.html"

    def get_queryset(self):
        return Reservation.objects.filter(
            team=self.request.user.team,
            end_date__gte=timezone.now(),
        )


class RoomListView(PermissionRequiredMixin, ListView):
    permission_required = "reservation.view_room"
    model = Room


class RoomCreateView(PermissionRequiredMixin, CreateView): ...


class RoomUpdateView(PermissionRequiredMixin, UpdateView): ...


class RoomDeleteView(PermissionRequiredMixin, DeleteView): ...


class ReservationListView(PermissionRequiredMixin, ListView): ...


class ReservationDetailView(PermissionRequiredMixin, DetailView): ...


class ReservationDeleteView(UserPassesTestMixin, DeleteView):
    model = Reservation
    success_url = reverse_lazy("index")

    def test_func(self) -> bool | None:
        reservation = self.get_object()
        user = self.request.user
        if user.has_perm("reservation.delete_reservation"):
            return True
        elif user.has_perm("reservation.delete_reservation_self_team") and user.team == reservation.team:
            return True
        else:
            return False
