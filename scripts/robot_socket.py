#!/usr/bin/python3
import json
import sys

import robot_deplacement as robot
import websocket


try:
    import thread
except ImportError:
    import _thread as thread

NOTIFY_MOVEMENT_EVENT = "movement_notification"



def perform_deplacement_mission(ws, actions):
    for action, arg in actions:
        if action == 'T':
            print("turning on " + str(arg) + "deg")
            robot.turn(arg)
        elif action == 'M':
            print("moving forward by " + str(arg) + "mm")
            robot.forward_by_millimeter(arg)
            ws.send(json.dumps({
                "event":  NOTIFY_MOVEMENT_EVENT,
                "isDone": False
            }))
        else:
            print("unknow action '" + str(action) + "'")
    ws.send(json.dumps({
        "event":  NOTIFY_MOVEMENT_EVENT,
        "isDone": True
    }))



def on_message(ws, message):
    print("### message ### : "+message)
    data = json.loads(message)
    if data["type"] == "deplacement":
        def run():
            perform_deplacement_mission(ws, data["actions"])
        thread.start_new_thread(run, ())



def on_error(ws, error):
    print(error)



def on_close(ws):
    print("### closed ###")



def on_open(ws):
    print("### open ###")
    with open("conf.json", "r") as jsonfile:
        data = jsonfile.read()
        ws.send(data)



def main():
    if len(sys.argv) != 2:
        print("usage: robot_socket websocketip")
        return
    websocket.enableTrace(True)
    uri = "ws://" + sys.argv[1] + "/robotsocket/"
    
    ws = websocket.WebSocketApp(uri,
                                on_message=on_message,
                                on_open=on_open,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()



if __name__ == "__main__":
    main()
