import datetime
from typing import Any
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from users.models import Team
from .models import Comment, Reservation, Room, Rating
from .forms import SubmitCommentForm, SubmitRatingForm, ReservationForm


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


class UserReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "index.html"

    def get_queryset(self):
        if self.request.user.id:
            return Reservation.objects.filter(
                team=self.request.user.team,
                end_date__gte=timezone.now(),
            )
        return None


class RoomListView(PermissionRequiredMixin, ListView):
    permission_required = "reservation.view_room"
    model = Room


class RoomCreateView(PermissionRequiredMixin, CreateView): ...


class RoomUpdateView(PermissionRequiredMixin, UpdateView): ...


class RoomDeleteView(PermissionRequiredMixin, DeleteView): ...


class ReservationListJson(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        today = datetime.datetime.now().date()
        date = request.GET.get("date")
        if not date:
            date = today
        reservations = Reservation.objects.filter(start_date__date=date)
        events = [
            {
                "id": reservation.id,
                "title": reservation.note,
                "start": reservation.start_date.isoformat(),
                "end": reservation.end_date.isoformat(),
                "resourceId": reservation.room.id,
                "backgroundColor": "green",
                "borderColor": "green",
            }
            for reservation in reservations
        ]
        return JsonResponse({"events": events}, safe=False)


class ReservationListView(LoginRequiredMixin, View):
    def get_data(self, request):
        resources = Room.objects.all()
        resources = [{"id": room.id, "title": room.name} for room in resources]
        return resources

    def get(self, request, *args, **kwargs):
        team = Team.objects.all() if request.user.is_admin() else request.user.team
        form = ReservationForm(
            initial={"team": team, "room": Room.objects.all(), "reserver_user": request.user}, user=request.user
        )
        data = self.get_data(request)
        context = {"resources": data, "form": form, "user": request.user}
        return render(request, "reservation/reservation_list.html", context=context)

    def post(self, request, *args, **kwargs):
        form = ReservationForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
        else:
            errors = form.errors
            print(errors)
        data = self.get_data(request)
        context = {"resources": data[0], "perms": data[1], "form": form}
        return render(request, "reservation/reservation_list.html", context=context)


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
