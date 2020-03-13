Commands that need to be run at turtlebot startup :

```
roscore &
roslaunch turtlebot3_bringup turtlebot3_core.launch &
```

command to start programme :
```
rosrun robotmissions robot_socket.py
```

to start all in one :

```
roscore &
sleep 30
roslaunch turtlebot3_bringup turtlebot3_core.launch &
sleep 30
rosrun robotmissions robot_socket.py

```
