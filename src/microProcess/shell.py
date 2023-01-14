from constants import *
from base_micro import BaseMicro
import serial
import cmd
import struct
import matplotlib.pyplot as plt


def binary(num):
    return int(''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num)), 2)


def float_(var):
    num = f'{(32 - len(bin(int(var[1:].hex(), 16))[2:])) * "0"}{bin(int(var[1:].hex(), 16))[2:]}'
    return struct.unpack('!f', struct.pack('!I', int(num, 2)))[0]


cmds = {'prompt': '(RaspShell) > ', 'wait': (lambda self, type_: None)}


def command(func):
    cmds[f'do_{func.__name__[(func.__name__[0] == "_"):]}'] = func
    return func


def ranged_int(name, value: str, l_=0, h=16):
    b = not (value.isdigit() and l_ <= int(value) < h)
    if b:
        print(f'{name} must be an integer between {l_} and {h-1}')
    return b


def check_float(name, value: str):
    try:
        float(value)
        return False
    except ValueError:
        print(f'{name} must be a float')
        return True


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


def test_pair(lst):
    if len(lst) & 1:
        print('Arguments work by pairs')
        return True
    return False


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
    self.send(self.make_message(MOV, 0, ticks + 0x10000 * (ticks < 0)))
    self.wait(MOV)


move.__doc__ = f"""
Command: move
move [{MIN_TICKS} <= ticks < {MAX_TICKS}]
Robot will move algebraicly <ticks> ticks forward
"""


@command
@arg_number(2)
def motor_value(self, args):
    if ranged_int('motor_id', args[0]) or ranged_int('t', args[1], MIN_T_MS, MAX_T_MS):
        return
    m_id, t = map(int, args)
    self.send(self.make_message(MOT_VALUE, m_id, t))
    self.wait(MOT_VALUE)


motor_value.__doc__ = f"""
Command: motor_value
motor_value [0 <= motor_id < 16] [{MIN_T_MS} <= t < {MAX_T_MS}]
sets motor <motor_id> on position m + t * (M - n) / 65536 (linear interpolation)
m, M being minimal and maximal positions of the motor
"""


@command
@arg_number(2)
def motor_time(self, args):
    if ranged_int('motor_id', args[0]) or ranged_int('ms', args[1], MIN_T_MS, MAX_T_MS):
        return
    m_id, ms = map(int, args)
    self.send(self.make_message(MOT_TIME, m_id, ms))
    self.wait(MOT_TIME)


motor_time.__doc__ = f"""
Command: motor_time
motor_time [0 <= motor_id < 16] [{MIN_T_MS} <= ms < {MAX_T_MS}]
Rotates motor <motor_id> during <ms> ms at its velocity
"""


@command
def pumps(self, line):
    args = line.split()
    if any(ranged_int('pump_id', x) for x in args):
        return
    self.send(self.make_message(PUM, 0, sum(1 << int(x) for x in set(args))))
    self.wait(PUM)


pumps.__doc__ = """
Command: pumps
set_pumps *[0 <= pump_id < 16]
sets every pump in pump_ids on other will be off
"""


@command
def motors(self, line):
    args = line.split()
    if not len(args):
        return print("At least one pair of arguments is expected")
    if test_pair(args) or no_duplicate(args) or any(ranged_int('motor_id', x) or ranged_int('t', y, h=0x10000) for x, y in pair(args)):
        return
    self.send(self.make_message(MOTS, len(args) // 2, sum(1 << int(x) for x in args[::2])))
    for x, y in pair(args):
        self.send(self.make_message(MOTS_A, int(x), int(y)))
    self.wait(MOTS)


motors.__doc__ = f"""
Command: motors
motors *([0 <= motor_id < 16] [{MIN_T_MS} <= t < {MAX_T_MS}])
identical to motor_value, but for mulitple motors at once (no duplicates allowed).
Expects at least one pair.
"""


@command
@arg_number(2)
def set_var(self, args):
    if args[0] not in VAR_NAMES or check_float('value', args[1]):
        return
    self.send(self.make_message(VAR_SET, VAR_DICT[args[0]], binary(float(args[1]))))
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
        return
    self.send(self.make_message(VAR_GET, VAR_DICT[args[0]], 0))
    self.wait(VAR_GET)


get_var.__doc__ = """
Command: set_var
set_var [var_name] [value]
sets the variable <var_name> to <value> in the raspberry Pico chip
Available variables: 
{}
""".format(' - ' + '\n - '.join(VAR_DICT.keys()))


@command
@arg_number(0)
def track(self, arg):
    self.track = not self.track
    self.send(self.make_message(TRACK, self.track, 0))
    print(f'Track toggled to {self.track}')
    self.wait(TRACK)


track.__doc__ = """
Command: track
track
toggles the track mode of the pico
"""


@command
def _exit(self, line):
    return 1


BaseShell = type('BaseShell', (cmd.Cmd, BaseMicro), cmds)


class Shell(BaseShell):
    track = False
    receive = BaseMicro.receive

    def __init__(self, port, baudrate, log_level=NECESSARY):
        BaseShell.__init__(self)
        self.serial = serial.Serial(port, baudrate)
        self.serial.read(self.serial.in_waiting)
        self.log_level = log_level

    def wait(self, order_id):
        tracked_values = []
        waiting = True

        while waiting:
            v = self.receive()
            if order_id == VAR_GET and v[0] >> 4 == VAR:
                print(f'Variable {VAR_NAMES[v[0] & 0xf]} = {float_(v)}')
            elif v[0] >> 4 == TER and v[0] & 0xf == order_id:
                waiting = False
                if tracked_values:
                    if not self.track:
                        self.send(self.make_message(TRACK, self.track, 0))
                    else:
                        plt.plot(tracked_values)
                        plt.show()
            elif v[0] >> 4 == TRA:
                tracked_values.append(float_(v))

    def complete_set_var(self, text, line, begidx, endidx):
        if text:
            return [x for x in VAR_NAMES if x.startswith(text)]
        return VAR_NAMES

    def complete_get_var(self, text, line, begidx, endidx):
        if text:
            return [x for x in VAR_NAMES if x.startswith(text)]
        return VAR_NAMES


if __name__ == '__main__':
    import sys
    log = NECESSARY if len(sys.argv) < 3 else LOG_MODES.index(sys.argv[2])
    Shell(sys.argv[1], 115200, log).cmdloop()
