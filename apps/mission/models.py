from django.db import models

from ifc.models import IfcModel



class DeplacementMissionModel(models.Model):
    ifc = models.ForeignKey(IfcModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    floor = models.CharField(max_length=100)
    start_x = models.IntegerField(null=False)
    start_y = models.IntegerField(null=False)
    end_x = models.IntegerField(null=False)
    end_y = models.IntegerField(null=False)
    
    
    def to_dict(self):
        return dict(
            id=self.pk,
            ifc=self.ifc.to_dict(),
            floor=self.floor,
            start_x=self.start_x,
            start_y=self.start_y,
            end_x=self.end_x,
            end_y=self.end_y
        )
