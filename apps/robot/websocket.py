import json

import logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings

from robot.models import RobotModel


logger = logging.getLogger(__name__)



class RobotConsumer(WebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None
    
    
    def connect(self):
        self.accept()
    
    
    def receive(self, text_data=None, bytes_data=None):
        if self.model is None:
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError:
                self.close(code=3001)  # Invalid JSON
                return
            
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
            logger.warning(f"Robot {self.model.uuid} sent : {text_data}")
            # TODO com with robot
    
    
    def disconnect(self, code):
        if self.model:
            async_to_sync(self.channel_layer.group_discard)(str(self.model.uuid), self.channel_name)
            self.model.disconnect()
    
    
    def mission(self, event):
        message = event["text_data"]
        self.send(text_data=message)
