from time import sleep

import ev3dev.ev3 as ev3


DEGREE_SUCCESS_RATE = 0.92

METER_IN_MS = 8200

BRAKE_TYPES_LIST = [
    ("coast", "lets the motor continue to turn until stopped by friction"),
    ("hold", "an active, forceful effort to stop the motor turning"),
    ("brake", "passively and less forcefully tries to stop the motor turning"),
]
BRAKE_TYPE = "brake"
LEFT = ev3.LargeMotor('outB')
RIGHT = ev3.LargeMotor('outA')

LEFT.reset()
RIGHT.reset()

GYRO = ev3.GyroSensor()
GYRO.mode = 'GYRO-ANG'

SPEED = 250



def reset_gyro():
    GYRO.mode = 'GYRO-RATE'
    GYRO.mode = 'GYRO-ANG'



def set_succ_rate(succ_rate):
    global DEGREE_SUCCESS_RATE
    DEGREE_SUCCESS_RATE = succ_rate



def turn(d):
    diff = DEGREE_SUCCESS_RATE * d
    target = GYRO.angle + diff
    motor, motor_inv = (RIGHT, LEFT) if diff < 0 else (LEFT, RIGHT)
    motor.run_forever(speed_sp=SPEED)
    motor_inv.run_forever(speed_sp=-SPEED)
    if diff > 0:
        while GYRO.angle <= target:
            pass
    else:
        while GYRO.angle >= target:
            pass
    motor.stop(stop_action=BRAKE_TYPE)
    motor_inv.stop(stop_action=BRAKE_TYPE)



def forward(t):
    LEFT.run_timed(time_sp=t, speed_sp=SPEED, stop_action=BRAKE_TYPE)
    RIGHT.run_timed(time_sp=t, speed_sp=SPEED, stop_action=BRAKE_TYPE)
    sleep(1 + t // 1000)



def forward_by_millimeter(millimeter):
    meter = millimeter / 1000
    forward(meter * METER_IN_MS)
    

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
        "- T to turn",
        "- R to reset",
        "- S to change speed",
        "- B to change stop action",
        "- P to proceed on given path"
    ]
    while True:
        print('\n'.join(CHOICES))
        choice = input("Enter a choice : ")
        if choice in ['f', 'F']:
            time = int(input('Enter time (in milliseconds) : '))
            forward(time)
        elif choice in ['fd', 'FD', 'fD', 'Fd']:
            dist_millimeters = int(input('Enter distance (in millimeter) : '))
            forward_by_millimeter(dist_millimeters)
        elif choice in ['er', 'Er', 'ER', 'eR']:
            set_succ_rate(float(input('Enter new degree turn success rate : ')))
        elif choice in ['st', 'ST', 'St', 'sT']:
            print_state()
        elif choice in ['t', 'T']:
            deg = float(input('Enter angle (in degree) :'))
            turn(deg)
        elif choice in ['s', 'S']:
            SPEED = int(input('Enter speed :'))
        elif choice in ['r', 'R']:
            reset_gyro()
            print("GYRO angle = ", GYRO.angle)
        elif choice in ['b', 'B']:
            print("Types : ")
            for name, desc in BRAKE_TYPES_LIST:
                print("\n" + name + " : " + desc)
            brake_choice = input('Enter type choice : ')
            if brake_choice not in [name for name, desc in BRAKE_TYPES_LIST]:
                print("Not a valide choice, no change")
            else:
                BRAKE_TYPE = brake_choice
        elif choice in ['p', 'P']:
            path = parse_path(input(
                'Enter path, (ex "(\'T\', -90), (\'M\', 300.0), (\'T\', -45), (\'M\', 424.2)") :'))
            do_path(path)
        else:
            print("No valid choice, quitting ...")
            break
