from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
import json


class IfcModel(models.Model):
    name = models.CharField(max_length=100)
    graph = JSONField(null=False, default=dict)
    filePath = models.FilePathField(path=settings.IFC_FILES_DIR)

    @classmethod
    def parse(cls, ifc_content):
        # NEED ifcopenshell to create GRAPH from ifc content
        return json.dumps({})

    @classmethod
    def validate_ifc_file(cls, file):
        print("validation" + str(file.read()))
        return True
