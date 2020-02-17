from django.db import models

from ifc.models import IfcModel


class DeplacementMissionModel(models.Model):
    ifc = models.ForeignKey(IfcModel, on_delete=models.CASCADE)
    floor = models.CharField(max_length=100)
    start_space = models.CharField(max_length=100)
    end_space = models.CharField(max_length=100)
