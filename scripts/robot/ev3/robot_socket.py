#!/usr/bin/python3
import json
import sys
from time import sleep

import robot_deplacement as robot
import websocket


try:
    import thread
except ImportError:
    import _thread as thread

NOTIFY_MOVEMENT_EVENT = "movement_notification"
NOTIFY_END_EVENT = "end_notification"
TIME_BEFORE_END_EVENT = 1  # in seconds


# Send some data to the server
def send_data(ws, data):
    print("Sending", data)
    ws.send(json.dumps(data))


# Performs all the actions one by one for the mission
def perform_deplacement_mission(ws, actions):
    for action, arg in actions:
        if action == 'T':
            print("Turning on " + str(arg) + "deg")
            robot.turn(arg)
        elif action == 'M':
            print("Moving forward by " + str(arg) + "mm")
            robot.forward_by_millimeter(arg)
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
            robot.fix_rotation()
            perform_deplacement_mission(ws, data["actions"])
        thread.start_new_thread(run, ())


# Prints when an error occured
def on_error(ws, error):
    print(error)


# Prints when the connection is closed with the websocket
def on_close(ws):
    print("### closed ###")


# Prints when the connection is opened with the websocket
def on_open(ws):
    print("### open ###")
    with open("conf.json", "r") as jsonfile:
        data = jsonfile.read()
        ws.send(data)



def main():
    websocket.enableTrace(True)
    uri = "ws://35.210.237.250/robotsocket/"
    
    ws = websocket.WebSocketApp(uri,
                                on_message=on_message,
                                on_open=on_open,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()



if __name__ == "__main__":
    main()
