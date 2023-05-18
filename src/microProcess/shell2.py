import os

from base_micro import *
import cmd
import struct
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import json


class BaseShell(MicroManager, cmd.Cmd):
    prompt = '(RaspShell) > '
    track = odometry = False
    waiting = False
    waited_id = None
    x, y, h, axle_track = 0, 0, 0, AXLE_TRACK_1A
    old = 0, 0

    def __init__(self):
        MicroManager.__init__(self)
        cmd.Cmd.__init__(self)
        self.left, self.right = [], []
        self.vars = {name: None for name in VAR_NAMES}
        self.cool_downs = ()

    @staticmethod
    def float_to_int(num):
        # integer from the IEEE-754 representation of a float
        return sum(b << (8 * i) for i, b in enumerate(struct.pack('f', num)))

    @staticmethod
    def bytes_to_float(buffer):
        # float from its IEEE-754 representation with bytes
        return struct.unpack('!f', buffer)[0]

    @staticmethod
    def twos_complement(integer):
        return integer + 0x10000 * (integer < 0)

    def send(self, port, id_, comp, arg):
        if port not in self.serials:
            return print(f'{BOARDS[port]} is not connected')
        usb = self.serials[port]
        usb.send(usb.make_message(id_, comp, arg))
        return True

    def wait(self, id_):
        date = time.perf_counter()
        self.waited_id = id_
        self.waiting, cool_downs = True, self.cool_downs
        try:
            while self.waiting:
                if cool_downs and id_ in (MOV, ROT):
                    dt = time.perf_counter() - date
                    new_cool_downs = tuple(x for x in self.cool_downs if x > dt)
                    for _ in range(len(cool_downs) - len(new_cool_downs)):
                        self.send(PICO1, LID, 0, 0)
                    cool_downs = new_cool_downs
                self.scan_feedbacks()
        except KeyboardInterrupt:
            self.waiting = False
            if id_ in (MOV, ROT):
                self.send(PICO1, CAN, 0, 0)
                self.wait(CAN)

    def plot_movement(self, left_target, right_target):
        fig, ax = plt.subplots()
        ax.set_ylim(min(-right_target / 20, 2 * right_target), max(-right_target / 20, 2 * right_target))

        nb_points = 50
        self.left, self.right = [float('nan')] * nb_points, [float('nan')] * nb_points
        xs = tuple(range(nb_points))
        curves = (
            *ax.plot(xs, self.left), *ax.plot(xs, self.right), *ax.plot((0, nb_points), (right_target, right_target))
        )

        wheels = [0, 0]

        def update(*args):
            # for _ in range(20):
            #     self.serials[PICO1].wheel_update(int.to_bytes((wheels[0] << 16) | wheels[1], 5, 'big'))
            #     wheels[0] += 2
            #     wheels[1] += 4
            date = time.perf_counter()
            while time.perf_counter() - date < 1 / 60:
                self.scan_feedbacks()
            curves[0].set_data(xs, [-x if not (left_target + right_target) else x for x in self.left])
            curves[1].set_data(xs, self.right)
            return curves

        anim = FuncAnimation(fig, update, cache_frame_data=False)
        plt.show()

    def plot_odometry(self):
        self.x, self.y, self.h = 0., 0., 0.
        self.old = 0, 0
        try:
            while True:
                date = time.perf_counter()
                while time.perf_counter() - date < 1 / 60:
                    self.scan_feedbacks()
                print(f'\rX : {self.x:.03f} m, Y : {self.y:.03f} m , HEADING : {180 * self.h / math.pi:.03f} deg;  {self.old =}', end=' ' * 8)
                time.sleep(.2)
        except KeyboardInterrupt:
            print()


cmds = {}

# ---------------------------------------------- Micro subclasses ------------------------------------------------------


class ShellGeneric(GenericMicro):
    master: BaseShell

    def termination(self, message):
        if message[0] & 0xf == self.master.waited_id:
            self.master.waiting = False

    def var_get(self, message):
        f_ = self.master.bytes_to_float(message[1:])
        self.master.vars[VAR_NAMES[message[0] & 0xf]] = f_
        print(f'Variable {VAR_NAMES[message[0] & 0xf]} = {f_}')

    def wheel_update(self, message):
        if self.master.track:
            left = (message[1] << 8) + message[2]
            left -= 0x10000 * (left >= 0x8000)
            right = (message[3] << 8) + message[4]
            right -= 0x10000 * (right >= 0x8000)
            self.master.right = self.master.right[1:] + [right]
            self.master.left = self.master.left[1:] + [left]
        elif self.master.odometry:
            # tick positions for each wheel
            left, right = message[1] * 256 + message[2], message[3] * 256 + message[4]

            # Two's complement
            left -= 0x10000 * (left >= 0x8000)
            right -= 0x10000 * (right >= 0x8000)

            d_left, d_right = left - self.master.old[0], right - self.master.old[1]
            self.master.old = left, right

            left_arc, right_arc = (
                2 * math.pi * d_left * WHEEL_RADIUS / TICKS_PER_REVOLUTION,
                2 * math.pi * d_right * WHEEL_RADIUS / TICKS_PER_REVOLUTION
            )

            # straight movement
            if d_left == d_right:
                self.master.x += left_arc * math.cos(self.master.h)
                self.master.y += left_arc * math.sin(self.master.h)
                return

            # circular movement
            radius = .5 * self.master.axle_track * (d_left + d_right) / (d_right - d_left)
            angle = (right_arc - left_arc) / self.master.axle_track
            a0, a1 = self.master.h - math.pi * .5, self.master.h - math.pi * .5 + angle
            self.master.x += radius * (math.cos(a1) - math.cos(a0))
            self.master.y += radius * (math.sin(a1) - math.sin(a0))
            self.master.h += angle


class ShellMovement(MovementMicro, ShellGeneric):
    pass


class ShellAction(ActionMicro, ShellGeneric):
    pass


class ShellArduino(ArduinoMicro, ShellGeneric):
    pass


BaseShell.micro_classes = ShellMovement, ShellAction, ShellArduino

# -------------------------------------------------- Decorators --------------------------------------------------------


# decorator because I hate to write 'do_' before my command names
def command(func):
    name: str = func.__name__
    cmds[f'do_{name[name.startswith("_"):]}'] = func
    return func


def add_to_dict(func):
    cmds[func.__name__] = func
    return func


# decorator to check the number of arguments
def arg_number(nb):
    def decor(func):
        def new_func(self: BaseShell, line):
            args = line.split()
            if len(args) != nb:
                print(f'Expected {nb} argument{"s" * (nb > 0)} for command {func.__name__}')
                return
            return func(self, *args)
        new_func.__name__ = func.__name__
        return new_func
    return decor

# ------------------------------------------------- Value checkers -----------------------------------------------------


# checkers return True when there is a problem
def ranged_int(var_name: str, value: str, inf=0, sup=16):
    try:
        number = int(value)
    except ValueError:
        print(f'{var_name} must be a valid integer')
        return True
    check = not inf <= number < sup
    if check:
        print(f'{var_name} must be between {inf} and {sup-1}')
    return check


def check_float(var_name: str, value: str):
    try:
        float(value)
        return False
    except ValueError:
        print(f'{var_name} must be a floating point number')
        return True


# --------------------------------------------------- Commands ---------------------------------------------------------


@command
@arg_number(0)
def _exit(self: BaseShell):
    for usb in self.serials.values():
        usb.serial.close()
    return 1


@command
def lidar(self: BaseShell, line):
    args = line.split()
    if args[0] == 'reset':
        self.cool_downs = ()
        return
    elif args[0] == 'state':
        return print(*self.cool_downs, sep='\n')
    if len(args) != 2:
        return print(f'Expected 1 argument that is \'reset\' or \'state\' or 2 arguments for command lidar')
    delay, duration = args
    if check_float('delay', delay) or check_float('duration', duration):
        return
    self.cool_downs += (float(delay), float(delay) + float(duration))


@command
@arg_number(1)
def move(self: BaseShell, ticks: str):
    if ranged_int('ticks', ticks, MIN_TICKS, MAX_TICKS):
        return
    ticks = int(ticks)
    if self.track and self.send(PICO1, MOV, 0, self.twos_complement(ticks)):
        self.send(PICO1, TRACK, 0, 0)
        self.plot_movement(ticks, ticks)
        self.send(PICO1, CAN, 0, 0)
        self.send(PICO1, TRACK, 0, 0)
        self.wait(CAN)
        return
    if self.send(PICO1, MOV, 0, self.twos_complement(ticks)):
        self.wait(MOV)


@command
@arg_number(1)
def rotate(self: BaseShell, ticks: str):
    if ranged_int('ticks', ticks, MIN_TICKS, MAX_TICKS):
        return
    ticks = int(ticks)
    if self.track and self.send(PICO1, ROT, 0, self.twos_complement(ticks)):
        self.send(PICO1, TRACK, 0, 0)
        self.plot_movement(-ticks, ticks)
        self.send(PICO1, TRACK, 0, 0)
        return
    if self.send(PICO1, ROT, 0, self.twos_complement(ticks)):
        self.wait(ROT)


@command
@arg_number(2)
def arm(self: BaseShell, left, right):
    if ranged_int('left', left, MIN_TICKS, MAX_TICKS) or ranged_int('right', right, MIN_TICKS, MAX_TICKS):
        return
    left, right = int(left), int(right)
    if self.send(PICO2, ARM, 0, (self.twos_complement(left) << 16) | self.twos_complement(right)):
        self.wait(ARM)

@command
@arg_number(0)
def lockers(self: BaseShell):
    if self.send(PICO2, LOK, 0, 0):
        self.wait(LOK)



@command
def pumps(self: BaseShell, line):
    args = line.split()
    if any(ranged_int('pump_id', pump_id, 0, 8) for pump_id in args):
        return
    pump_ids = set(int(x) for x in args)
    if self.send(PICO2, PUM, 1, sum(1 << pump_id for pump_id in pump_ids)):
        self.wait(PUM)


@command
def motors(self: BaseShell, line):
    args = line.split()
    if any(ranged_int('motor_id', pump_id, 0, 8) for pump_id in args):
        return
    motor_ids = set(int(x) for x in args)
    if self.send(PICO2, PUM, 2, sum(1 << motor_id for motor_id in motor_ids)):
        self.wait(PUM)


@command
def solenoids(self: BaseShell, line):
    args = line.split()
    if any(ranged_int('solenoid_id', pump_id, 0, 8) for pump_id in args):
        return
    solenoid_ids = set(int(x) for x in args)
    if self.send(PICO2, PUM, 4, sum(1 << solenoid_id for solenoid_id in solenoid_ids)):
        self.wait(PUM)


@command
@arg_number(1)
def _get(self: BaseShell, var_name: str):
    if var_name not in VAR_DICT:
        return print(f'Unknown variable {var_name}')
    if self.send(VAR_DESTINATION[VAR_DICT[var_name]], VAR_GET, VAR_DICT[var_name], 0):
        self.wait(VAR_GET)


@add_to_dict
def complete_get(self, text, line, begin, end):
    if text:
        return [x for x in VAR_NAMES if x.startswith(text)]
    return VAR_NAMES


@command
@arg_number(2)
def _set(self: BaseShell, var_name: str, value: str):
    if var_name not in VAR_DICT:
        return print(f'Unknown variable {var_name}')
    if check_float('value', value):
        return
    if self.send(VAR_DESTINATION[VAR_DICT[var_name]], VAR_SET, VAR_DICT[var_name], self.float_to_int(float(value))):
        self.wait(VAR_SET)


@add_to_dict
def complete_set(self, text, line, begin, end):
    if text:
        return [x for x in VAR_NAMES if x.startswith(text)]
    return VAR_NAMES


@command
@arg_number(0)
def variables(self: BaseShell):
    for name in VAR_NAMES:
        _get(self, name)


@command
@arg_number(1)
def save(self: BaseShell, file_name):
    print("Saving...")
    variables(self, '')
    with open(os.path.join('saved_sessions', f"{file_name}.json"), 'w') as f:
        json.dump(self.vars, f)
    print('Saved.')


@add_to_dict
def complete_save(self, text, line, begin, end):
    if text:
        return [x[:-5] for x in os.listdir('saved_sessions') if x.startswith(text) and x.endswith('.json')]
    return [x[:-5] for x in os.listdir('saved_sessions') if x.endswith('.json')]


@command
@arg_number(1)
def load(self: BaseShell, file_name):
    print("Loading ...")
    with open(os.path.join('saved_sessions', f"{file_name}.json"), 'r') as f:
        self.vars = json.load(f)
    for var_name, value in self.vars.items():
        if value is None:
            continue
        _set(self, f'{var_name} {value}')

    print('Loaded.')


@add_to_dict
def complete_load(self, text, line, begin, end):
    if text:
        return [x[:-5] for x in os.listdir('saved_sessions') if x.startswith(text) and x.endswith('.json')]
    return [x[:-5] for x in os.listdir('saved_sessions') if x.endswith('.json')]


@command
@arg_number(0)
def track(self: BaseShell):
    self.track = not self.track
    print(f'Tracking toggled to {self.track}')


@command
@arg_number(0)
def odometry(self: BaseShell):
    self.odometry, self.track = True, False
    self.send(PICO1, TRACK, 0, 0)
    self.plot_odometry()
    self.send(PICO1, TRACK, 0, 0)

@command
@arg_number(1)
def log_mode(self: BaseShell, mode: str):
    self.log_level = LOG_MODES.index(mode)


@add_to_dict
def complete_log_mode(self, text, line, begin, end):
    if text:
        return [x for x in LOG_MODES if x.startswith(text)]
    return LOG_MODES


@command
@arg_number(0)
def reset(self: BaseShell):
    for s in self.serials.values():
        s.serial.close()
    self.serials = self.reset()


Shell = type('Shell', (BaseShell,), cmds)

if __name__ == '__main__':
    Shell().cmdloop()
