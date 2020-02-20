from django.db import models

from ifc.models import PositionModel



class RobotStatusModel(models.Model):
    battery = models.DecimalField(max_digits=20, decimal_places=2)
    rotation = models.DecimalField(max_digits=20, decimal_places=2)

    def to_dict(self):
        return dict(
            id=self.pk, battery=self.battery, rotation=self.rotation)


class RobotModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    position = models.ForeignKey(PositionModel, on_delete=models.CASCADE)
    status = models.ForeignKey(RobotStatusModel, on_delete=models.CASCADE,
                               null=True)  # can be null before any comm with the robot

    def to_dict(self):
        return dict(
            id=self.pk,
            name=self.name,
            position=self.position.to_dict(),
            status=self.status.to_dict() if self.status else None)
