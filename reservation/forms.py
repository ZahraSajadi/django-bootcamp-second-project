from typing import Any
from django import forms
from .models import Comment, Rating
from django.forms.widgets import NumberInput


class SubmitRatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["value"]
        widgets = {"value": NumberInput(attrs={"max": 5, "min": 1})}

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
