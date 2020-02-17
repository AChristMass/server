from django.forms import Form, CharField, IntegerField


class DeplacementMissionForm(Form):
    ifc_id = IntegerField()
    floor = CharField(max_length=100)
    start_space = CharField(max_length=100)
    end_space = CharField(max_length=100)
