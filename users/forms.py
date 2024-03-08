from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Team
from second_project.settings import TEAM_LEADERS_GROUP_NAME

User = get_user_model()


class TeamCreateUpdateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by("id").all(),
        required=False,
        label="Members",
        widget=forms.CheckboxSelectMultiple,
    )
    leader = forms.ModelChoiceField(queryset=User.objects.none(), required=False, label="Team Leader")

    class Meta:
        model = Team
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.instance)
        if self.instance and self.instance.pk:
            team_members = self.instance.customuser_set.all()
            self.fields["leader"].queryset = team_members
            self.fields["members"].initial = team_members
            self.fields["leader"].initial = self.instance.leader

    def save(self, commit=True):
        team = super().save(commit=commit)
        if commit:
            team_leader_group = Group.objects.get(name=TEAM_LEADERS_GROUP_NAME)
            previous_leader = team.customuser_set.filter(groups=team_leader_group).first()
            leader = self.cleaned_data.get("leader")
            if leader != previous_leader:
                if previous_leader:
                    team_leader_group.user_set.remove(previous_leader)
                if leader:
                    team_leader_group.user_set.add(leader)
            members = set(self.cleaned_data["members"])
            current_members = set(team.customuser_set.all())

            for member in members - current_members:
                member.team = team
                if commit:
                    member.save()

            for user in current_members - members:
                user.team = None
                if commit:
                    user.save()
        return team
