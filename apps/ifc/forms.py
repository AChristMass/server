from django.forms import Form, FileField, CharField

from ifc.models import IfcModel


class IfcForm(Form):
    name = CharField(min_length=1, max_length=100)
    ifc_file = FileField(validators=[IfcModel.validate_ifc_file])
