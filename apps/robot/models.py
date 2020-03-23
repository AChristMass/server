import logging

from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


# This class represents the status of a robot
class RobotStatusModel(models.Model):
    battery = models.DecimalField(max_digits=20, decimal_places=2)
    rotation = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Returns the data in a dictionary
    def to_dict(self):
        return dict(battery=self.battery, rotation=self.rotation)


# This class represents a robot with its attributes
class RobotModel(models.Model):
    uuid = models.UUIDField(primary_key=True, null=False, editable=False)
    name = models.CharField(max_length=50)
    type = models.CharField(null=False, choices=zip(settings.ROBOT_CONFIGS.keys(),
                                                    settings.ROBOT_CONFIGS.keys()),
                            max_length=10)
    connected = models.BooleanField(default=False)
    channel_name = models.CharField(null=False, max_length=64)
    status = models.ForeignKey(RobotStatusModel, on_delete=models.CASCADE, null=True)
    
    
    def delete(self, using=None, keep_parents=False):
        super().delete()
    
    # Connects the robot to the server
    def connect(self, channel_name):
        logger.log(logging.WARNING, f"Robot connected : {self.uuid}")
        self.channel_name = channel_name
        self.connected = True
        self.save()
    
    # Disconnects the robot from the server
    def disconnect(self):
        logger.log(logging.WARNING, f"Robot disconnected : {self.uuid}")
        self.connected = False
        self.save()
    
    # Returns the robot's data in a dictionary
    def to_dict(self):
        return dict(
            uuid=self.pk,
            name=self.name,
            type=self.type,
            connected=self.connected,
            status=self.status.to_dict() if self.status else None)
    
    # Returns all the robots that are connected to the server
    @classmethod
    def robots_connected(cls):
        return cls.objects.all().filter(connected=True)
