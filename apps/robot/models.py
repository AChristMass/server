from django.db import models

from ifc.models import IfcModel


class RobotPositionModel(models.Model):
    ifc = models.ForeignKey(IfcModel, on_delete=models.CASCADE)
    floor = models.CharField(max_length=100)
    x = models.DecimalField(max_digits=20, decimal_places=2)
    y = models.DecimalField(max_digits=20, decimal_places=2)

    def as_json(self):
        return dict(
            id=self.pk,
            ifc=self.ifc.as_json(),
            floor=self.floor,
            x=self.x,
            y=self.y
        )


class RobotStatusModel(models.Model):
    battery = models.DecimalField(max_digits=20, decimal_places=2)
    rotation = models.DecimalField(max_digits=20, decimal_places=2)

    def as_json(self):
        return dict(
            id=self.pk, battery=self.battery, rotation=self.rotation)


class RobotModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    position = models.ForeignKey(RobotPositionModel, on_delete=models.CASCADE)
    status = models.ForeignKey(RobotStatusModel, on_delete=models.CASCADE,
                               null=True)  # can be null before any comm with the robot

    def as_json(self):
        return dict(
            id=self.pk,
            name=self.name,
            position=self.position.as_json(),
            status=self.status.as_json() if self.status else None)
