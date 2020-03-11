import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils.timezone import now

from robot.models import RobotModel


logger = logging.getLogger(__name__)



class RobotConsumer(WebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None
        self.mission_in_prog = None
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
            logger.info(f"Connected robot {self.model.uuid}")
            UserConsumer.broadcast({
                "type":  "robot_connected",
                "robot": self.model
            })
            async_to_sync(self.channel_layer.group_add)(str(self.model.uuid), self.channel_name)
            self.send(text_data="ok")
        else:
            logger.warning(f"Robot {self.model.uuid} sent : {data}")
            self.__getattribute__(data["event"])(data)  # command from robot to socket
    
    
    def disconnect(self, code):
        logger.info(f"Disconnecting robot {self.model.uuid}")
        if self.model:
            async_to_sync(self.channel_layer.group_discard)(str(self.model.uuid), self.channel_name)
            self.model.disconnect()
        self.free()
    
    # command from robot
    def movement_notification(self, data):
        x, y = self.data["path"].pop(0)
        logger.info(f"movement notification {x,y}")
        self.mission_in_prog.x = x
        self.mission_in_prog.y = y
        if "isDone" in data:
            logger.info(f"mission done")
            self.free()
        else:
            self.mission_in_prog.save()
            mission_channel = settings.MISSION_CHANNEL + str(self.mission_in_prog.pk)
            logger.info(f"update mission {mission_channel}")
            async_to_sync(self.channel_layer.group_send)(mission_channel, {
                    "type":    "update_mission",
                    "mission": self.mission_in_prog
                })
    
    
    def mission_start(self, event):
        if self.mission_in_prog is not None and not self.mission_in_prog.is_done:
            return  # a mission is already running
        self.mission_in_prog = event["mission"]
        logger.info(f"Robot {self.model.uuid} starting mission {self.mission_in_prog.mission.pk}")
        self.data = event["data"]["socket"]
        self.send(text_data=json.dumps(event["data"]["robot"]))
    
    
    def free(self):
        logger.info(f"freeing robot socket")
        self.mission_in_prog.is_done = True
        self.mission_in_prog.ended_at = now()
        self.mission_in_prog.save()
        async_to_sync(self.channel_layer.group_send)(
            settings.MISSION_CHANNEL + str(self.mission_in_prog.pk), {
                "type":    "update_mission",
                "mission": self.mission_in_prog
            })
        self.mission_in_prog = None
        self.data = {}



class UserConsumer(WebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(settings.USER_CHANNEL, self.channel_name)
    
    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(settings.USER_CHANNEL, self.channel_name)
    
    
    def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            self.close(code=3001)  # Invalid JSON
            return
        if "missionId" in data:
            async_to_sync(self.channel_layer.group_add)(
                settings.MISSION_CHANNEL + str(data["missionId"]), self.channel_name)
    
    
    @classmethod
    def broadcast(cls, message):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(settings.USER_CHANNEL, message)
    
    
    def robot_connected(self, event):
        robot = event["robot"]
        self.send(text_data=json.dumps(
            {
                "action": "robot_connection",
                "robot":  robot.to_dict()
            }))
    
    
    def update_mission(self, event):
        mission = event["mission"]
        if mission.is_done:
            async_to_sync(self.channel_layer.group_discard)(
                settings.MISSION_CHANNEL + str(mission.pk), self.channel_name)
        self.send(text_data=json.dumps(
            {
                "action":  "update_mission",
                "mission": mission.to_dict()
            }))
