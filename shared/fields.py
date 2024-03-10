from django.forms import ModelMultipleChoiceField


class UserMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        text = f"{obj}"
        if obj.team:
            text = f"{text} - {obj.team}"
        return text
