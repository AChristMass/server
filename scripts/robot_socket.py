#!/usr/bin/python3
import asyncio
import sys
import websockets



async def main_loop(ws):
    while True:
        data = await ws.recv()



async def connect_robot(ip, port):
    uri = f"ws://{ip}:{port}/robotsocket/"
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
    if len(sys.argv) != 3:
        print("usage: robot_socket address port")
        return
    asyncio.get_event_loop().run_until_complete(connect_robot(sys.argv[1], sys.argv[2]))



if __name__ == "__main__":
    main()
