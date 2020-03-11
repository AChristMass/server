from django.db import models

from ifc.models import IfcModel
from robot.models import RobotModel



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
            name=self.name,
            ifc=self.ifc.to_dict(),
            floor=self.floor,
            start_x=self.start_x,
            start_y=self.start_y,
            end_x=self.end_x,
            end_y=self.end_y
        )



class MissionInProgModel(models.Model):
    mission = models.ForeignKey(DeplacementMissionModel, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(auto_now_add=True)
    robot = models.ForeignKey(RobotModel, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)
    x = models.IntegerField(null=False)
    y = models.IntegerField(null=False)
    
    
    def to_dict(self):
        return dict(
            id=self.pk,
            robot=self.robot.to_dict(),
            mission=self.mission.to_dict(),
            started_at=self.started_at,
            ended_at=self.ended_at,
            is_done=self.is_done,
            x=self.x,
            y=self.y,
        )
