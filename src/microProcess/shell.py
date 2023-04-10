from constants import *
from base_micro import BaseMicro
import serial
import cmd
import struct
import time
import matplotlib.pyplot as plt
import os
import json


def float_to_int(num):
    # integer from the IEEE-754 representation of a float
    return sum(b << (8 * i) for i, b in enumerate(struct.pack('f', num)))


def bytes_to_float(buffer):
    # IEEE-754 representation of a float from bytes
    return struct.unpack('!f', buffer)[0]


# prepares cmd.Cmd inheritance
cmds = {'prompt': '(RaspShell) > '}


# decorator because I hate to write 'do_' before my command names
def command(func):
    cmds[f'do_{func.__name__[(func.__name__[0] == "_"):]}'] = func
    return func


# Verifies if arguments are in a given range
def ranged_int(name, value: str, l_=0, h=16):
    b = not ((value.isdigit() or (value[1:].isdigit() and value[0] == '-')) and l_ <= int(value) < h)
    if b:
        print(f'{name} must be an integer between {l_} and {h-1}')
    return b


# Verifies if the arguement can be converted to float
def check_float(name, value: str):
    try:
        float(value)
        return False
    except ValueError:
        print(f'{name} must be a float')
        return True


# decorator to check the number of arguments
def arg_number(nb):
    def decor(f):
        def fun(self, line):
            args = line.split()
            if len(args) != nb:
                print(f'Expected {nb} argument{"s" * (nb > 0)} for command {f.__name__}')
                return
            return f(self, args)
        fun.__name__ = f.__name__
        return fun
    return decor


# Verifies if arguements are given by pair
def test_pair(lst):
    if len(lst) & 1:
        print('Arguments work by pairs')
        return True
    return False


# Divides a list into pairs
def pair(lst):
    for i in range(0, len(lst), 2):
        yield lst[i], lst[i+1]


def no_duplicate(lst):
    if len(set(lst[::2])) != len(lst) // 2:
        print('No duplicates are allowed in motor_id')
        return True
    return False


@command
@arg_number(1)
def rotate(self, args):
    if ranged_int('ticks', args[0], MIN_TICKS, MAX_TICKS):
        return
    ticks = int(args[0])
    self.command = ticks
    self.right_wheel = []
    self.left_wheel = []
    if self.track:
        self.send(self.make_message(TRACK, 1, 0))
    self.send(self.make_message(ROT, 0, ticks + 0x10000 * (ticks < 0)))
    self.wait(ROT)


rotate.__doc__ = f"""
Command: rotate
rotate [{MIN_TICKS} <= ticks < {MAX_TICKS}]
Robot will rotate around its center for <ticks> ticks (clockwise: ticks < 0, couterclockwise: ticks > 0)
"""


@command
@arg_number(1)
def move(self, args):
    if ranged_int('ticks', args[0], MIN_TICKS, MAX_TICKS):
        return
    ticks = int(args[0])
    self.command = ticks
    self.right_wheel = []
    self.left_wheel = []
    if self.track:
        self.send(self.make_message(TRACK, 1, 0))
    self.send(self.make_message(MOV, 0, ticks + 0x10000 * (ticks < 0)))
    self.wait(MOV)


move.__doc__ = f"""
Command: move
move [{MIN_TICKS} <= ticks < {MAX_TICKS}]
Robot will move algebraicly <ticks> ticks forward
"""


@command
@arg_number(2)
def arm(self, args):
    left, right = args
    if ranged_int('left', left, MIN_TICKS, MAX_TICKS) or ranged_int('right', right, MIN_TICKS, MAX_TICKS):
        return
    left, right = int(left), int(right)
    left, right = left + 0x10000 * (left < 0), right + 0x10000 * (right < 0)
    self.send(self.make_message(ARM, 0, (left << 16) | right))
    self.wait(ARM)


arm.__doc__ = f"""
Command: arm
arm [{MIN_TICKS} <= left < {MAX_TICKS}]  [{MIN_TICKS} <= right < {MAX_TICKS}]
Move 1A's robot arm left motor moves by <left> ticks, right motor moves by <right> ticks 
"""


# @command
# @arg_number(2)
# def motor_value(self, args):
#     if ranged_int('motor_id', args[0]) or ranged_int('t', args[1], MIN_T_MS, MAX_T_MS):
#         return
#     m_id, t = map(int, args)
#     self.send(self.make_message(MOT_VALUE, m_id, t))
#     self.wait(MOT_VALUE)
#
#
# motor_value.__doc__ = f"""
# Command: motor_value
# motor_value [0 <= motor_id < 16] [{MIN_T_MS} <= t < {MAX_T_MS}]
# sets motor <motor_id> on position m + t * (M - n) / 65536 (linear interpolation)
# m, M being minimal and maximal positions of the motor
# """


# @command
# @arg_number(2)
# def motor_time(self, args):
#     if ranged_int('motor_id', args[0]) or ranged_int('ms', args[1], MIN_T_MS, MAX_T_MS):
#         return
#     m_id, ms = map(int, args)
#     self.send(self.make_message(MOT_TIME, m_id, ms))
#     self.wait(MOT_TIME)
#
#
# motor_time.__doc__ = f"""
# Command: motor_time
# motor_time [0 <= motor_id < 16] [{MIN_T_MS} <= ms < {MAX_T_MS}]
# Rotates motor <motor_id> during <ms> ms at its velocity
# """


@command
def pumps(self, line):
    args = line.split()
    if any(ranged_int('pump_id', x, 0, 4) for x in args):
        return
    self.send(self.make_message(PUM, 1, sum(1 << int(x) for x in set(args))))
    self.wait(PUM)


@command
def motors(self, line):
    args = line.split()
    if any(ranged_int('motor_id', x, 0, 4) for x in args):
        return
    self.send(self.make_message(PUM, 2, sum(1 << int(x) for x in set(args)) << 8))
    self.wait(PUM)


@command
def solenoids(self, line):
    args = line.split()
    if any(ranged_int('solenoid_id', x, 0, 4) for x in args):
        return
    self.send(self.make_message(PUM, 4, sum(1 << int(x) for x in set(args)) << 16))
    self.wait(PUM)


pumps.__doc__ = """
Command: pumps
pumps *[0 <= pump_id < 4]
sets every pump in pump_ids on, others will be off
"""


# @command
# def motors(self, line):
#     args = line.split()
#     if not len(args):
#         return print("At least one pair of arguments is expected")
#     if test_pair(args) or no_duplicate(args) or any(ranged_int('motor_id', x) or ranged_int('t', y, h=0x10000) for x, y in pair(args)):
#         return
#     self.send(self.make_message(MOTS, len(args) // 2, sum(1 << int(x) for x in args[::2])))
#     for x, y in pair(args):
#         self.send(self.make_message(MOTS_A, int(x), int(y)))
#     self.wait(MOTS)
#
#
# motors.__doc__ = f"""
# Command: motors
# motors *([0 <= motor_id < 16] [{MIN_T_MS} <= t < {MAX_T_MS}])
# identical to motor_value, but for mulitple motors at once (no duplicates allowed).
# Expects at least one pair.
# """


@command
@arg_number(2)
def set_var(self, args):
    if args[0] not in VAR_NAMES:
        print(f'Unknown variable {args[0]}')
        return
    if check_float('value', args[1]):
        return
    self.send(self.make_message(VAR_SET, VAR_DICT[args[0]], float_to_int(float(args[1]))))
    self.wait(VAR_SET)


set_var.__doc__ = """
Command: set_var
set_var [var_name] [value]
sets the variable <var_name> to <value> in the raspberry Pico chip
Available variables: 
{}
""".format(' - ' + '\n - '.join(VAR_DICT.keys()))


@command
@arg_number(1)
def get_var(self, args):
    if args[0] not in VAR_NAMES:
        print(f'Unknown variable {args[0]}')
        return
    self.send(self.make_message(VAR_GET, VAR_DICT[args[0]], 0))
    self.wait(VAR_GET)


get_var.__doc__ = """
Command: get_var
get_var [var_name]
gets the variable <var_name> from the raspberry Pico chip
Available variables: 
{}
""".format(' - ' + '\n - '.join(VAR_NAMES))


@command
@arg_number(0)
def track(self, arg):
    self.track = not self.track
    print(f'Track toggled to {self.track}')


track.__doc__ = """
Command: track
track
toggles the track mode of the pico
"""


@command
def _exit(self, line):
    return 1


@command
@arg_number(2)
def lidar(self, args):
    delay, duration = args
    if check_float('delay', delay) or check_float('duration', duration):
        return
    self.lidar_stops.append((float(delay), float(duration)))


lidar.__doc__ = """
Command: lidar
lidar [delay] [duration]
Next movement order will be interrupted by a lidar stop after <delay> s for <duration> s
Can be used multiple times
"""


@command
@arg_number(0)
def show_vars(self, args):
    for i in range(len(VAR_NAMES)):
        self.send(self.make_message(VAR_GET, i, 0))
        self.wait(VAR_GET)


@command
@arg_number(1)
def save_vars(self, args):
    vars_ = []
    for i in range(len(VAR_NAMES)):
        self.send(self.make_message(VAR_GET, i, 0))
        self.wait(VAR_GET)
        vars_.append(self.last_received_var)
    with open(f'./saved_sessions/{args[0]}.json', 'w') as f:
        json.dump(vars_, f)


@command
@arg_number(1)
def load_vars(self, args):
    with open(f'./saved_sessions/{args[0]}.json', 'r') as f:
        vars_ = json.load(f)
    for i, var in enumerate(vars_):
        print(f'Variable {VAR_NAMES[i]} = {var}')
        self.send(self.make_message(VAR_SET, i, float_to_int(var)))


@command
@arg_number(0)
def synchronise(self, args):
    self.synchronise()


@command
@arg_number(0)
def waiting_bytes(self, args):
    print(f"Number of waiting bytes: {self.serial.in_waiting}")


BaseShell = type('BaseShell', (cmd.Cmd, BaseMicro), cmds)


class Shell(BaseShell):
    track = False
    waiting = False
    waited_id = None
    last_movement = None
    last_received_var = 0.

    def __init__(self, port, log_level=NECESSARY):
        self.log_level = log_level
        BaseShell.__init__(self)
        self.serial = serial.Serial(port, BAUDRATE)
        self.synchronise()
        self.tracked_values = []
        self.lidar_stops = []
        self.left_wheel, self.right_wheel = [], []
        self.command = 0

    def var_get(self, message):
        self.last_received_var = bytes_to_float(message[1:])
        print(f'Variable {VAR_NAMES[message[0] & 0xf]} = {bytes_to_float(message[1:])}')

    def terminaison(self, message):
        #  the waited order is finished
        if message[0] & 0xf == self.waited_id:
            self.waiting = False
            if self.tracked_values:
                if self.track and message[0] & 0xf in (MOV, ROT, CAN):
                    self.send(self.make_message(TRACK, 0, 0))
                    plt.plot(self.tracked_values)
                    plt.show()
                self.tracked_values = []
            if self.right_wheel:
                self.serial.read(self.serial.in_waiting)
                if self.track and message[0] & 0xf in (MOV, ROT, CAN):
                    self.send(self.make_message(TRACK, 0, 0))
                    plt.plot(self.right_wheel, label='Right Wheel')
                    plt.plot([(-x if self.last_movement == ROT else x) for x in self.left_wheel], label='Left Wheel')
                    plt.plot((0, len(self.left_wheel)), (self.command,) * 2, label='Left target')
                    plt.plot((0, len(self.left_wheel)), (self.command,) * 2, label='Right target')
                    plt.legend()
                    plt.show()
                self.right_wheel = []
                self.left_wheel = []

    def wheel_update(self, message):
        left = (message[1] << 8) + message[2]
        right = (message[3] << 8) + message[4]
        self.right_wheel.append(right - 0x10000 * (right >= 0x1000))
        self.left_wheel.append(left - 0x10000 * (left >= 0x1000))

    def tracked(self, message):
        self.tracked_values.append(bytes_to_float(message[1:]))

    def wait(self, order_id):
        # waits for the terminaison of the given order_id
        self.waited_id = order_id
        self.waiting = True

        date, stops, restarts = 0., (), ()
        if self.lidar_stops and order_id in (MOV, ROT):
            stops, restarts = map(list, zip(*((t, t + dt) for t, dt in self.lidar_stops)))
            date = time.perf_counter()

        while self.waiting:
            try:
                if self.lidar_stops and self.waited_id in (MOV, ROT):
                    dt = time.perf_counter() - date
                    for o, lid in enumerate((stops, restarts)):
                        pop = []
                        for i, delay in enumerate(lid):
                            if delay < dt:
                                pop.insert(0, i)
                                self.send(self.make_message(LID, o, 0))
                        for i in pop:
                            lid.pop(i)
                if self.serial.in_waiting:
                    self.feedback(self.receive())
            except KeyboardInterrupt:
                if self.waited_id in (MOV, ROT):
                    self.send(self.make_message(CAN, 0, 0))
                    self.waited_id = CAN
                    self.last_movement = self.waited_id
                    print(f'{type(self).__name__} : info : Now waiting for CANCEL terminaison')

                else:
                    self.waiting = False

    def complete_set_var(self, text, line, begidx, endidx):
        if text:
            return [x for x in VAR_NAMES if x.startswith(text)]
        return VAR_NAMES

    complete_get_var = complete_set_var

    def complete_save_vars(self, text, line, begidx, endidx):
        if text:
            return [x for x in os.listdir('./saved_sessions') if x.startswith(text)]
        return os.listdir('./saved_sessions')

    complete_load_vars = complete_save_vars


if __name__ == '__main__':
    import sys
    p = sys.argv[1]
    if not os.path.exists('./saved_sessions'):
        os.mkdir('./saved_sessions')
    level = LOG_MODES.index(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in LOG_MODES else NOTHING
    Shell(p, level).cmdloop()
