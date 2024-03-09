from typing import Any
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Team
from second_project.settings import TEAM_LEADERS_GROUP_NAME

User = get_user_model()


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        text = f"{obj}"
        if obj.team:
            text = f"{text} - {obj.team}"
        return text


class TeamCreateUpdateForm(forms.ModelForm):
    members = UserMultipleChoiceField(
        queryset=User.objects.order_by("id").all(),
        required=False,
        label="Members",
        widget=forms.CheckboxSelectMultiple,
    )
    leader = forms.ModelChoiceField(queryset=User.objects.all(), required=False, label="Team Leader")

    class Meta:
        model = Team
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["leader"].limit_choices_to = {"team__id": self.instance.pk}
        if self.instance and self.instance.pk:
            team_members = self.instance.customuser_set.all()
            self.fields["members"].initial = set(team_members)
            self.fields["leader"].initial = self.instance.get_leader()
        else:
            self.fields["members"].initial = set()

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["previous_leader"] = self.fields["leader"].initial
        members = set(self.cleaned_data["members"])
        current_members = self.fields["members"].initial
        cleaned_data["new_members"] = members - current_members
        cleaned_data["removed_members"] = current_members - members - {cleaned_data["leader"]}

        return cleaned_data

    def save(self, commit=True):
        team = super().save(commit=commit)
        new_members = self.cleaned_data["new_members"]
        removed_members = self.cleaned_data["removed_members"]
        leader = self.cleaned_data["leader"]
        previous_leader = self.cleaned_data["previous_leader"]
        team_leader_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
        for member in new_members:
            member.team = team
        for user in removed_members:
            user.team = None
        if leader:
            leader.team = team
        if commit:
            for member in new_members:
                member.save()
            for user in removed_members:
                user.save()
            if leader != previous_leader:
                team_leader_group.user_set.remove(previous_leader)
                if leader:
                    team_leader_group.user_set.add(leader)
                    leader.save()
        return team
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class UserCreateForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone', 'profile_image', 'email', 'password', 'password']
