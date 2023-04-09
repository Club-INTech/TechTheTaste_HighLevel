import serial

from base_micro import *
from serial.tools.list_ports import comports
from constants import *
import math


def empty():
    return
    yield


class MicroProcess(BaseMicro):
    last = 0, 0

    def __init__(self, port, lidar, main, robot_x, robot_y, robot_heading, axle_track, log=NECESSARY):
        self.log_level = log
        self.serial = serial.Serial(port, BAUDRATE)
        self.synchronise()

        self.lidar, self.main = lidar, main
        # Routines corresponding to order types MOVEMENT and ACTION
        self.routines = [empty(), empty()]

        self.robot_x, self.robot_y = robot_x, robot_y
        self.robot_heading = robot_heading
        self.robot_axle_track = axle_track
        self.run()

    def next(self, type_):
        if self.log_level > N_NEC:
            print(f'{type(self).__name__} : info : Next step of routine {self.routines[type_]}({CATEGORIES[type_]})')
        # goes through the routine of the given type (MOVEMENT or ACTION)
        try:
            next_order = next(self.routines[type_])
            self.send(self.make_message(*next_order))
            # if next_order[0] == MOTS: # deprecated
            #     for _ in range(next_order[1]):
            #         next_order = next(self.routines[type_])
            #         self.send(self.make_message(*next_order))
        # routine is finished
        except StopIteration:
            self.pull(type_)

    def termination(self, message):
        t = TYPES[message[0] & 0xf]
        if t != OTHER:
            self.next(t)

    def wheel_update(self, message):
        # tick offset for each wheel
        left, right = message[1] * 256 + message[2], message[3] * 256 + message[4]

        # Two's complement
        left -= 0x10000 * (left >= 0x8000)
        right -= 0x10000 * (right >= 0x8000)

        left_arc, right_arc = (
            2 * math.pi * left * WHEEL_RADIUS / TICKS_PER_REVOLUTION,
            2 * math.pi * right * WHEEL_RADIUS / TICKS_PER_REVOLUTION
        )

        # straight movement
        if left == right:
            self.robot_pos[0] += left_arc * math.cos(self.robot_heading)
            self.robot_pos[1] += left_arc * math.sin(self.robot_heading)
            return

        # circular movement
        radius = .5 * self.robot_axle_track * (left + right) / (right - left)
        angle = (right_arc - left_arc) / self.robot_axle_track
        a0, a1 = self.robot_heading - math.pi * .5, self.robot_heading - math.pi * .5 + angle
        self.robot_x.value += radius * (math.cos(a1) - math.cos(a0))
        self.robot_y.value += radius * (math.sin(a1) - math.sin(a0))
        self.robot_heading.value += angle

    def pull(self, type_):
        if self.log_level > N_NEC:
            print(f'{type(self).__name__} : info : Asking next routine ({CATEGORIES[type_]})')
        # asks for a new routine of a given type
        self.main.send(type_)

    def _loop(self):
        if self.lidar.poll():
            self.send(self.make_message(LID, self.lidar.recv(), 0))
        if self.main.poll():
            type_, gen, args = self.main.recv()
            self.routines[type_] = gen(*args)
            self.next(type_)
        if self.serial.in_waiting:
            self.feedback(self.receive())

    def run(self):
        try:
            self.pull(ACTION)
            self.pull(MOVEMENT)
            while True:
                self._loop()
        except KeyboardInterrupt:
            self.send(self.make_message(CAN, 0, 0))
            self.serial.close()


class GenericMicro(BaseMicro):
    id_ = -1

    def __init__(self, serial_, master):
        self.master = master
        self.serial = serial_

    @classmethod
    def new(cls, old):
        return cls(old.serial, old.master)

    @property
    def log_level(self):
        return self.master.log_level

    @property
    def log_method(self):
        return self.master.log_method

    def identify(self, message):
        self.id_ = message[0] & 0xf


class MovementMicro(GenericMicro):
    pass


class ActionMicro(GenericMicro):
    pass


class ArduinoMicro(GenericMicro):
    pass


MICRO_CLASSES = MovementMicro, ActionMicro, ArduinoMicro


class MicroManager:
    log_method = print
    log_level = NECESSARY

    def __init__(self):
        serials = tuple(
            GenericMicro(serial.Serial(usb.usb_description(), BAUDRATE), self) for usb in comports()
        )

        for s in serials:
            s.pre_sync()
        time.sleep(1.)
        for index, s in enumerate(serials):
            s.clear_buffer()
            s.send(s.make_message(ID, 0, 0))

        # identifies all serial connections
        # any port that is not responding within 5 secs will be discarded
        date = time.perf_counter()
        while any(s.id_ == -1 for s in serials) and time.perf_counter() - date < 5.:
            for s in serials:
                if s.serial.in_waiting:
                    s.feedback(s.receive())

        for s in serials:
            if s.id_ != -1 or self.log_level <= NEC:
                continue
            self.log_method(f'{type(self).__name__} : info : Could not identify hardware on {s.serial.portstr}')

        self.serials = {
            s.id_: MICRO_CLASSES[s.id_].new(s) for s in serials if s.id_ != -1
        }

    def scan_feedbacks(self):
        for s in self.serials.values():
            if s.serial.in_waiting:
                s.feedback(s.receive())


class NewMicroProcess(MicroManager):
    def __init__(self, lida_pipe, main_pipe):
        self.main_pipe, self.lidar_pipe = main_pipe, lida_pipe
        MicroManager.__init__(self)
