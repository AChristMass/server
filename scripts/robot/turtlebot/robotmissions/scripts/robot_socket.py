#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from math import radians
import websocket
from time import sleep
import json

try:
    import thread
except ImportError:
    import _thread as thread

# This file contains all the function that are being called to control the Turtlebot

pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
rospy.init_node('node_name')

SPEED_DEG_SEC = 10  # rotation speed in deg/s
SPEED_RAD_SEC = radians(SPEED_DEG_SEC)

SPEED_MET_SEC = 0.2  # move speed in m/s

# Function to turn the robot
def turn(ang_deg):
    wait_time = ang_deg / SPEED_DEG_SEC
    twist = Twist()
    twist.angular.z = SPEED_RAD_SEC
    pub.publish(twist)
    sleep(wait_time)
    twist.angular.z = 0
    pub.publish(twist)

# Function to make the robot move forward for a distance
def forward(dist_mm):
    meters = dist_mm / 1000
    wait_time = meters / SPEED_MET_SEC
    twist = Twist()
    twist.linear.x = SPEED_MET_SEC
    pub.publish(twist)
    sleep(wait_time)
    twist.linear.x = 0
    pub.publish(twist)


NOTIFY_MOVEMENT_EVENT = "movement_notification"
NOTIFY_END_EVENT = "end_notification"
TIME_BEFORE_END_EVENT = 1  # in seconds

# Send data to the server
def send_data(ws, data):
    print("Sending", data)
    ws.send(json.dumps(data))


# Parse the actions to perform the mission and call the right functions
def perform_deplacement_mission(ws, actions):
    for action, arg in actions:
        if action == 'T':
            print("Turning on " + str(arg) + "deg")
            turn(arg)
        elif action == 'M':
            print("Moving forward by " + str(arg) + "mm")
            forward(arg)
            send_data(ws, {"event": NOTIFY_MOVEMENT_EVENT})
        else:
            print("unknow action '" + str(action) + "'")
    print("Wait " + str(TIME_BEFORE_END_EVENT) + " seconds")
    sleep(TIME_BEFORE_END_EVENT)  # wait before sending end event
    send_data(ws, {"event": NOTIFY_END_EVENT})


# Prints when a message is received
def on_message(ws, message):
    print("### message ### : " + message)
    data = json.loads(message)
    if data["type"] == "deplacement":
        def run():
            perform_deplacement_mission(ws, data["actions"])
        thread.start_new_thread(run, ())


# Prints when an error occured
def on_error(ws, error):
    print(error)


# Prints when the connection with the websocket is closed
def on_close(ws):
    print("### closed ###")


# Prints when the connection with the websocket is opened
def on_open(ws):
    print("### open ###")
    with open("conf.json", "r") as jsonfile:
        data = jsonfile.read()
        ws.send(data)




if not rospy.is_shutdown():
    websocket.enableTrace(True)
    uri = "ws://35.210.237.250/robotsocket/"
    
    ws = websocket.WebSocketApp(uri,
                                on_message=on_message,
                                on_open=on_open,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()


