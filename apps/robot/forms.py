from django import forms


class RobotForm(forms.Form):
    ifc_id = forms.IntegerField()
    floor = forms.CharField(max_length=100)
    x = forms.DecimalField(max_digits=20, decimal_places=2)
    y = forms.DecimalField(max_digits=20, decimal_places=2)
    name = forms.CharField(max_length=100)
