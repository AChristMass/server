from django import forms


class RobotForm(forms.Form):
    uuid = forms.UUIDField()
