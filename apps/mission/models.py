from django.db import models

from ifc.models import IfcModel



class DeplacementMissionModel(models.Model):
    ifc = models.ForeignKey(IfcModel, on_delete=models.CASCADE)
    floor = models.CharField(max_length=100)
    start_x = models.IntegerField(null=False)
    start_y = models.IntegerField(null=False)
    end_x = models.IntegerField(null=False)
    end_y = models.IntegerField(null=False)
