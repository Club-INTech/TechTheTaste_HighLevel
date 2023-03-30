from base_micro import *
from constants import * 
import math              


def empty():
    return
    yield



class MicroProcess(BaseMicro):

    def __init__(self, port, lidar, main, robot_x, robot_y, robot_heading, axle_track, log=NECESSARY):
        self.serial = serial.Serial(port, BAUDRATE)
        self.log_level = log

        self.lidar, self.main = lidar, main
        # Routines corresponding to order types MOVEMENT and ACTION
        self.routines = [empty(), empty()]

        self.robot_x, self.robot_y = robot_x, robot_y
        self.robot_heading = robot_heading
        self.robot_axle_track = axle_track

    def next(self, type_):
        if self.log_level > N_NEC:
            print(f'{type(self).__name__} : info : Next step of routine {self.routines[type_]}({CATEGORIES[type_]})')
        # goes through the routine of the given type (MOVEMENT or ACTION)
        try:
            next_order = next(self.routines[type_])
            self.send(self.make_message(*next_order))
            if next_order[0] == MOTS:
                for _ in range(next_order[1]):
                    next_order = next(self.routines[type_])
                    self.send(self.make_message(*next_order))
        # routine is finished
        except StopIteration:
            self.pull(type_)

    def terminaison(self, message):
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
            print(self.main.recv())
            type_, gen = self.main.recv()
            self.routines[type_] = gen()
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
