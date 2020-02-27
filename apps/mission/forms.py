from django.forms import Form, CharField, IntegerField, UUIDField



class DeplacementMissionForm(Form):
    ifc_id = IntegerField()
    floor = CharField(max_length=100)
    start_space = CharField(max_length=100)
    end_space = CharField(max_length=100)



class SendMissionForm(Form):
    robot_uuid = UUIDField()
