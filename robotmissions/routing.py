from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from robot.connect import RobotConsumer


application = ProtocolTypeRouter({
    "websocket": URLRouter([url(r"^robotsocket/", RobotConsumer, name="robot_connect")])
})
