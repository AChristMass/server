### Needed package installation 

```
pip3 install websocket-client
```

### Running command 

```
python3 robot_socket.py
```

### Troubleshoot

##### Your server is located elsewhere 

Websocket url is hardcoded to ws://35.210.237.250/robotsocket/, 
modify it in the main to your server url

##### Your robot rotation/translation are not accurate

You will have to calibrate your robot.
To do this you have to modify globals in robot_deplacement.py 
```
DEGREE_SUCCESS_RATE  # success rate of a rotation with positive angle
DEGREE_SUCCESS_RATE_NEG  # success rate of a rotation with negative angle
METER_IN_MS  # time in milliseconds that your robot take to move of 1m
```

For this you can run 
```
python3 robot_deplacement.py
```
on your robot and try with different values until you found accurate ones.
