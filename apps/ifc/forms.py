from django.forms import Form, FileField, CharField, IntegerField

from ifc.models import IfcModel


class IfcForm(Form):
    name = CharField(min_length=1, max_length=100)
    ifc_file = FileField(validators=[IfcModel.validate_ifc_file])


class IfcModifyForm(Form):
    id = IntegerField()
    name = CharField(min_length=1, max_length=100)
    ifc_file = FileField(required=False, validators=[IfcModel.validate_ifc_file])
