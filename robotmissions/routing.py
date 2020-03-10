from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from robot.websocket import RobotConsumer, UserConsumer


application = ProtocolTypeRouter({
    "websocket": URLRouter([url(r"^robotsocket/", RobotConsumer, name="robot_connect"),
                            url(r"^usersocket/", UserConsumer, name="user_connect")])
})

