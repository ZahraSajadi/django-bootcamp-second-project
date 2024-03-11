from django import forms
from .fields import UserMultipleChoiceField


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.__class__ not in [
                UserMultipleChoiceField,
                forms.MultipleChoiceField,
                forms.CheckboxSelectMultiple,
                forms.CheckboxInput,
            ]:
                field.widget.attrs.update({"class": "form-control", "style": "width: 300px;"})
