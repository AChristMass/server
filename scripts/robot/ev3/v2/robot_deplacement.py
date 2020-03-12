from time import sleep

from ev3dev2.motor import MoveSteering, MoveTank, OUTPUT_A, OUTPUT_B
from ev3dev2.sensor import INPUT_2
from ev3dev2.sensor.lego import GyroSensor


OUT_LEFT = OUTPUT_B
OUT_RIGHT = OUTPUT_A

MOVE_TANK = MoveTank(OUT_LEFT, OUT_RIGHT)
MOVE_STEERING = MoveSteering(OUT_LEFT, OUT_RIGHT)

DEGREE_SUCCESS_RATE = 0.92
DEGREE_SUCCESS_RATE_NEG = 0.88

METER_IN_MS = 8200

BRAKE_TYPES_LIST = [
    ("coast", "lets the motor continue to turn until stopped by friction"),
    ("hold", "an active, forceful effort to stop the motor turning"),
    ("brake", "passively and less forcefully tries to stop the motor turning"),
]
BRAKE_TYPE = "brake"

GYRO = GyroSensor(INPUT_2)
GYRO.mode = 'GYRO-ANG'

SPEED = 25  # in percent



def forward(t):
    print("start")
    wait_time = t / 1000  # in seconds
    nb_wait = wait_time / 0.1  # nb of wait of 0.1second
    start_ang = GYRO.angle
    print("nb_wait", nb_wait)
    for i in range(int(nb_wait)):
        ang = GYRO.angle
        delta_ang = start_ang - ang
        st = delta_ang * 10
        print("steering", st)
        MOVE_STEERING.on(steering=st, speed=SPEED)
        sleep(0.1)
    MOVE_STEERING.off()
    sleep(1)



def forward_by_millimeter(millimeter):
    meter = millimeter / 1000
    forward(meter * METER_IN_MS)

def set_succ_rate_neg(succ_rate):
    global DEGREE_SUCCESS_RATE_NEG
    DEGREE_SUCCESS_RATE_NEG = succ_rate

def reset_gyro():
    GYRO.reset()



def set_succ_rate(succ_rate):
    global DEGREE_SUCCESS_RATE
    DEGREE_SUCCESS_RATE = succ_rate



def turn(d):
    if d > 0:
        delta = DEGREE_SUCCESS_RATE * d
    else:
        delta = DEGREE_SUCCESS_RATE_NEG * d
    print("delta", delta)
    print("angle start", GYRO.angle)
    steering = -100 if delta < 0 else 100
    MOVE_STEERING.on(steering=steering, speed=SPEED)
    GYRO.wait_until_angle_changed_by(delta, direction_sensitive=True)
    print("angle end", GYRO.angle)
    MOVE_STEERING.off()



def print_state():
    print('SPEED = ', SPEED)
    print('METER_IN_MS = ', METER_IN_MS)
    print('DEGREE_SUCCESS_RATE = ', DEGREE_SUCCESS_RATE)
    for name, desc in BRAKE_TYPES_LIST:
        if name == BRAKE_TYPE:
            print('BRAKE_TYPE = ', name, desc)
    print('GYRO ANGLE = ', GYRO.angle)



def _parse_path(txt):
    path = []
    elem_list = txt.replace('(', '').split('),')
    for elem in elem_list:
        action = elem.replace(' ', '').replace(')', '').replace("'", '').split(',')
        act_type = action[0]
        act_arg = float(action[1])
        path.append((act_type, act_arg))
    return path



def do_actions(actions):
    for action, arg in actions:
        if action == 'T':
            print("turning on " + str(arg) + "deg")
            turn(arg)
        elif action == 'M':
            print("moving forward by " + str(arg) + "mm")
            forward_by_millimeter(arg)
        else:
            print("unknow action '" + str(action) + "'")



if __name__ == '__main__':
    print_state()
    
    CHOICES = [
        "- F to move forward (by time)",
        "- FD to move forward (by distance in millimeters)",
        "- ST to print state",
        "- ER to change degree success rate",
        "- ERN to change negative degree success rate",
        "- T to turn",
        "- R to reset",
        "- S to change speed",
        "- B to change stop action",
        "- P to proceed on given path"
    ]
    while True:
        print('\n'.join(CHOICES))
        choice = input("Enter a choice : ").lower()
        if choice == 'f':
            time = int(input('Enter time (in milliseconds) : '))
            forward(time)
        elif choice == 'fd':
            dist_millimeters = int(input('Enter distance (in millimeter) : '))
            forward_by_millimeter(dist_millimeters)
        elif choice == 'er':
            set_succ_rate(float(input('Enter new degree turn success rate : ')))
        elif choice == 'ern':
            set_succ_rate_neg(float(input('Enter new negative degree turn success rate : ')))
        elif choice == 'st':
            print_state()
        elif choice == 't':
            deg = float(input('Enter angle (in degree) :'))
            turn(deg)
        elif choice == 's':
            SPEED = int(input('Enter speed :'))
        elif choice == 'r':
            reset_gyro()
            print("GYRO angle = ", GYRO.angle)
        elif choice == 'b':
            print("Types : ")
            for name, desc in BRAKE_TYPES_LIST:
                print("\n" + name + " : " + desc)
            brake_choice = input('Enter type choice : ')
            if brake_choice not in [name for name, desc in BRAKE_TYPES_LIST]:
                print("Not a valide choice, no change")
            else:
                BRAKE_TYPE = brake_choice
        else:
            print("No valid choice, quitting ...")
            break
