import json
from json import JSONDecodeError

from channels.generic.websocket import WebsocketConsumer

from robot.models import RobotModel, ROBOT_TYPES



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
            except JSONDecodeError:
                self.close(code=3001)  # Invalid JSON
                return
            
            if "uuid" not in data or "type" not in data:
                self.close(code=3002)  # JSON must have fields : uuid, type
                return
            
            if data["type"] not in ROBOT_TYPES:
                self.close(code=3003)  # Robot type not handled
                return
            
            try:
                self.model = RobotModel.objects.get(uuid=data["uuid"])
            except RobotModel.DoesNotExist:
                self.model = RobotModel.objects.create(uuid=data["uuid"], type=data["type"])
            self.model.connect()
            self.send(text_data="ok")
        else:
            pass  # TODO
    
    
    def disconnect(self, code):
        if self.model:
            self.model.disconnect()
