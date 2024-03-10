from datetime import datetime, timezone, time, timedelta
from typing import Any
from django import forms

from .models import Comment, Rating, Reservation
from django.forms.widgets import NumberInput
from django.db.models import Q


class SubmitRatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["value"]
        widgets = {"value": NumberInput(attrs={"class": "form-control", "max": 5, "min": 1, "style": "width: 100px;"})}

    def clean_value(self):
        value = self.cleaned_data["value"]
        if value < 1 or value > 5:
            raise forms.ValidationError("Rate must be beetwen 1 and 5.")
        else:
            return value

    def save(self, commit: bool = True) -> Any:
        rate = super().save(commit=False)
        rate_db = Rating.objects.filter(user=rate.user, room=rate.room).first()
        if rate_db:
            value = rate.value
            rate = rate_db
            rate.value = value
        if commit:
            rate.save()
        return rate


class SubmitCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {"content": forms.Textarea(attrs={"class": "form-control", "rows": 3, "style": "width: 500px;"})}


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        exclude = ["pk"]
        widgets = {
            "reserver_user": forms.HiddenInput(attrs={"id": "reserver_user", "name": "reserver_user"}),
            "start_date": forms.TextInput(
                attrs={"class": "input", "id": "start-time", "name": "start-time", "placeholder": "Select time..."}
            ),
            "end_date": forms.TextInput(
                attrs={"class": "input", "id": "end-time", "name": "end-time", "placeholder": "Select time..."}
            ),
            "note": forms.Textarea(
                attrs={"id": "note", "name": "note", "placeholder": "Dont forget the tea!!!", "rows": 3, "cols": 25}
            ),
            "team": forms.Select(attrs={"id": "reserve-team", "name": "reserve-team"}),
            "room": forms.Select(attrs={"id": "reserve-room", "name": "reserve-room"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if not self.user.is_admin():
            self.fields["team"].widget = forms.HiddenInput(attrs={"id": "reserve-team", "name": "reserve-team"})

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        room = cleaned_data.get("room")
        team = cleaned_data.get("team")
        now = datetime.now(timezone.utc)
        overlapping_reservations = None

        if start and end:
            start_time = start.time()
            end_time = end.time()
            if end <= start:
                raise forms.ValidationError("End date must be greater than start date.")
            if start.date() != end.date():
                raise forms.ValidationError("Start and end dates must be on the same day.")
            if start_time < time(7) or end_time > time(22):
                raise forms.ValidationError("Both start and end times should be between 7 am and 10 pm.")
            if end <= now:
                raise forms.ValidationError("The reservation time is not valid.")
            overlapping_reservations = Reservation.objects.filter(
                Q(room=room)
                & (
                    Q(start_date__range=(start, end - timedelta(seconds=1)))
                    | Q(end_date__range=(start + timedelta(seconds=1), end))
                )
            )
        if overlapping_reservations:
            raise forms.ValidationError("Overlapping Reservation!")

        if not self.user.is_admin():
            if not self.user.is_team_leader():
                raise forms.ValidationError("Permission denied!")
            elif self.user.team != team:
                raise forms.ValidationError("Permission denied!")

        return cleaned_data
