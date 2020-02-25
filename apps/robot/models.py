from django.db import models
import logging


ROBOT_TYPES = {
    "ev3": "ev3"
}

logger = logging.getLogger(__name__)



class RobotStatusModel(models.Model):
    battery = models.DecimalField(max_digits=20, decimal_places=2)
    rotation = models.DecimalField(max_digits=20, decimal_places=2)
    
    
    def to_dict(self):
        return dict(
            id=self.pk, battery=self.battery, rotation=self.rotation)



class RobotModel(models.Model):
    uuid = models.UUIDField(primary_key=True, null=False, editable=False)
    type = models.CharField(null=False, choices=zip(ROBOT_TYPES.keys(), ROBOT_TYPES.values()),
                            max_length=10)
    connected = models.BooleanField(default=False)
    status = models.ForeignKey(RobotStatusModel, on_delete=models.CASCADE, null=True)
    
    
    def connect(self):
        logger.log(logging.INFO, f"Robot connected : {self.uuid}")
        self.connected = True
        self.save()
    
    
    def disconnect(self):
        logger.log(logging.INFO, f"Robot disconnected : {self.uuid}")
        self.connected = False
        self.save()
    
    
    def to_dict(self):
        return dict(
            id=self.pk,
            name=self.name,
            position=self.position.to_dict(),
            status=self.status.to_dict() if self.status else None)
