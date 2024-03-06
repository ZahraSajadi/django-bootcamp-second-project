from django import forms
from .models import CustomUser


class SignUpForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'email', 'password', 'team', 'profile_image']
        widgets = {
            'password': forms.PasswordInput(),
        }
