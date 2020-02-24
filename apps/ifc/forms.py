from django.forms import CharField, FileField, Form

from ifc.models import IfcModel



class IfcForm(Form):
    name = CharField(min_length=1, max_length=100)
    ifc_file = FileField(validators=[IfcModel.validate_ifc_file])



class IfcModifyForm(Form):
    name = CharField(required=False, min_length=1, max_length=100)
    ifc_file = FileField(required=False, validators=[IfcModel.validate_ifc_file])
