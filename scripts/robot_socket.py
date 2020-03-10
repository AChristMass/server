#!/usr/bin/python3
import asyncio
import json
import sys

import robot_deplacement as robot
import websockets


NOTIFY_MOVEMENT_EVENT = "movement_notification"



async def perform_deplacement_mission(ws, actions):
    for action, arg in actions:
        if action == 'T':
            print("turning on " + str(arg) + "deg")
            robot.turn(arg)
        elif action == 'M':
            print("moving forward by " + str(arg) + "mm")
            robot.forward_by_millimeter(arg)
            await ws.send(json.dumps({
                "event":  NOTIFY_MOVEMENT_EVENT,
                "isDone": False
            }))
        else:
            print("unknow action '" + str(action) + "'")
    await ws.send(json.dumps({
        "event":  NOTIFY_MOVEMENT_EVENT,
        "isDone": True
    }))



async def main_loop(ws):
    while True:
        print("WAITING FOR NEW DATA")
        data = await ws.recv()
        data = json.loads(data)
        if data["type"] == "deplacement":
            await perform_deplacement_mission(ws, data["actions"])



async def connect_robot(ip):
    uri = "ws://" + ip + "/robotsocket/"
    print("uri : ", uri)
    with open("conf.json", "r") as jsonfile:
        data = jsonfile.read()
    
    async with websockets.connect(uri) as ws:
        await ws.send(data)
        data = await ws.recv()
        if data == "ok":
            print("Robot is now connected")
            await main_loop(ws)
        else:
            print("Robot failed to connect")
            return



def main():
    if len(sys.argv) != 2:
        print("usage: robot_socket websocketip")
        return
    asyncio.get_event_loop().run_until_complete(connect_robot(sys.argv[1]))



if __name__ == "__main__":
    main()
