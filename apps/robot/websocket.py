import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.utils.timezone import now

from robot.models import RobotModel


logger = logging.getLogger(__name__)



class RobotConsumer(WebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None
        self.mission = None
        self.data = {}
    
    
    def connect(self):
        self.accept()
    
    
    def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            self.close(code=3001)  # Invalid JSON
            return
        if self.model is None:
            if "uuid" not in data or "type" not in data:
                self.close(code=3002)  # JSON must have fields : uuid, type
                return
            
            if data["type"] not in settings.ROBOT_CONFIGS:
                self.close(code=3003)  # Robot type not handled
                return
            
            try:
                self.model = RobotModel.objects.get(uuid=data["uuid"])
            except RobotModel.DoesNotExist:
                self.model = RobotModel.objects.create(uuid=data["uuid"], type=data["type"])
            self.model.connect(self.channel_name)
            async_to_sync(self.channel_layer.group_add)(str(self.model.uuid), self.channel_name)
            self.send(text_data="ok")
        else:
            logger.warning(f"Robot {self.model.uuid} sent : {data}")
            # TODO com with robot
            self.__getattribute__(data["event"])(data)
    
    
    def disconnect(self, code):
        if self.model:
            async_to_sync(self.channel_layer.group_discard)(str(self.model.uuid), self.channel_name)
            self.model.disconnect()
        self.free()
    
    
    def movement_notification(self, data):
        x, y = self.data["path"].pop(0)
        self.mission.x = x
        self.mission.y = y
        
        if data["isDone"]:
            self.free()
        else:
            self.mission.save()
    
    
    def mission(self, event):
        if self.mission is not None and not self.mission.is_done:
            return  # mission already running
        self.mission = event["mission"]
        self.data = event["data"]["socket"]
        self.send(text_data=json.dumps(event["data"]["robot"]))
    
    
    def free(self):
        self.mission.is_done = True
        self.mission.ended_at = now()
        self.mission.save()
        self.mission = None
        self.data = {}
