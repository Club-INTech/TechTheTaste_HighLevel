from base_micro import *
from constants import *
import math


def empty():
    return
    yield


class MicroProcess(BaseMicro):
    last = 0, 0

    def __init__(self, port, lidar, main, robot_x, robot_y, robot_heading, axle_track, log=MINIMAL):
        self.log_level = log
        self.serial = serial.Serial(port, BAUDRATE)
        self.synchronise()

        self.last = [None, None]
        self.lidar, self.main = lidar, main
        # Routines corresponding to order types MOVEMENT and ACTION
        self.routines = [empty(), empty()]

        self.robot_x, self.robot_y = robot_x, robot_y
        self.robot_heading = robot_heading
        self.robot_axle_track = axle_track
        self.run()

    def next(self, type_):
        if self.log_level > NOT_NECESSARY:
            print(f'{type(self).__name__} : info : Next step of routine {self.routines[type_].__name__}({CATEGORIES[type_]})')
        # goes through the routine of the given type (MOVEMENT or ACTION)
        try:
            next_order = next(self.routines[type_])
            self.last[type_] = next_order[0]
            self.send(self.make_message(*next_order))
        # routine is finished
        except StopIteration:
            self.pull(type_)

    def termination(self, message):
        t = TYPES[message[0] & 0xf]
        if t != OTHER and self.last[t] == message[0] & 0xf:
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
            self.robot_x.value += left_arc * math.cos(self.robot_heading.value)
            self.robot_y.value += left_arc * math.sin(self.robot_heading.value)
            return

        # circular movement
        radius = .5 * self.robot_axle_track * (left + right) / (right - left)
        angle = (right_arc - left_arc) / self.robot_axle_track
        a0, a1 = self.robot_heading - math.pi * .5, self.robot_heading.value - math.pi * .5 + angle
        self.robot_x.value += radius * (math.cos(a1) - math.cos(a0))
        self.robot_y.value += radius * (math.sin(a1) - math.sin(a0))
        self.robot_heading.value += angle

    def pull(self, type_):
        if self.log_level > NOT_NECESSARY:
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


class NewMicroProcess(MicroManager):
    axle_track = AXLE_TRACK_1A

    def __init__(self, lida_pipe, main_pipe, robot_x, robot_y, robot_heading):
        self.robot_x, self.robot_y, self.robot_heading = robot_x, robot_y, robot_heading
        self.main_pipe, self.lidar_pipe = main_pipe, lida_pipe
        MicroManager.__init__(self)

        self.last = [0, 0]
        self.routines = [empty(), empty()]

    def scan_feedbacks(self):
        if self.lidar_pipe.poll():
            pass
        if self.main_pipe.poll():
            type_, gen, args = self.main_pipe.recv()
            self.routines[type_] = gen(*args)
        MicroManager.scan_feedbacks(self)

    def terminate(self, order_id, order_type):
        pass

    def next(self, type_):
        if self.log_level > NOT_NECESSARY:
            print(f'{type(self).__name__} : info : Next step of routine {self.routines[type_].__name__}({CATEGORIES[type_]})')
        # goes through the routine of the given type (MOVEMENT or ACTION)
        try:
            id_, comp, arg = next(self.routines[type_])
            self.last[type_] = id_
            if DESTINATION[id_] in self.serials:
                port = self.serials[DESTINATION[id_]]
                port.send(port.make_message(id_, comp, arg))
        # routine is finished
        except StopIteration:
            self.pull(type_)


class MPGenericMicro(GenericMicro):
    master: NewMicroProcess

    def termination(self, message):
        order_id = message[0] & 0xf
        self.master.terminate(order_id, self.id_)


class MPMovement(MovementMicro, MPGenericMicro):
    old_wheel = 0., 0.

    def wheel_update(self, message):
        # tick positions for each wheel
        left, right = message[1] * 256 + message[2], message[3] * 256 + message[4]
        # Two's complement
        left -= 0x10000 * (left >= 0x8000)
        right -= 0x10000 * (right >= 0x8000)

        d_left, d_right = left - self.old_wheel[0], right - self.old_wheel[1]
        self.old_wheel = left, right

        left_arc, right_arc = (
            2 * math.pi * d_left * WHEEL_RADIUS / TICKS_PER_REVOLUTION,
            2 * math.pi * d_right * WHEEL_RADIUS / TICKS_PER_REVOLUTION
        )

        # straight movement
        if d_left == d_right:
            self.master.robot_x.value += left_arc * math.cos(self.master.robot_heading)
            self.master.robot_y.value += left_arc * math.sin(self.master.robot_heading)
            return

        # circular movement
        radius = .5 * self.master.axle_track * (d_left + d_right) / (d_right - d_left)
        angle = (right_arc - left_arc) / self.master.axle_track
        a0, a1 = self.master.robot_heading - math.pi * .5, self.master.robot_heading - math.pi * .5 + angle
        self.master.robot_x.value += radius * (math.cos(a1) - math.cos(a0))
        self.master.robot_y.value += radius * (math.sin(a1) - math.sin(a0))
        self.master.robot_heading.value += angle


class MPArduinoMicro(ArduinoMicro, MPGenericMicro):
    pass
