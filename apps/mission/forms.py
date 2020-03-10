from django.forms import Form, CharField, IntegerField, UUIDField



class DeplacementMissionForm(Form):
    ifc_id = IntegerField()
    name = CharField(max_length=50)
    floor = CharField(max_length=100)
    start_x = IntegerField()
    start_y = IntegerField()
    end_x = IntegerField()
    end_y = IntegerField()



class SendMissionForm(Form):
    robot_uuid = UUIDField()
