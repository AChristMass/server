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
    channel_name = models.CharField(null=False, max_length=64)
    status = models.ForeignKey(RobotStatusModel, on_delete=models.CASCADE, null=True)
    
    
    def connect(self, channel_name):
        logger.log(logging.WARNING, f"Robot connected : {self.uuid}")
        self.channel_name = channel_name
        self.connected = True
        self.save()
    
    
    def disconnect(self):
        logger.log(logging.WARNING, f"Robot disconnected : {self.uuid}")
        self.connected = False
        self.save()
    
    
    def to_dict(self):
        return dict(
            uuidid=self.pk,
            connected=self.connected,
            status=self.status.to_dict() if self.status else None)
