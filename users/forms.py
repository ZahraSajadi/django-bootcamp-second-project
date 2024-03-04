from django import forms


class LoginForm(forms.Form):
    phone = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone"}),
    )
