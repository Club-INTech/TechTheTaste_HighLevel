from constants import *


def goto(angle, magnitude):
    yield CAN, 0, 0
    yield ROT, 0, angle + 0x10000 * (angle < 0)
    yield MOV, 0, magnitude + 0x10000 * (magnitude < 0)


def stop():
    yield CAN, 0, 0


def move_cake():
    pass


def place_cherry():
    pass


class RoutineSender:
    def __init__(self, robot_x, robot_y, robot_heading, micro_pipe, axle_track):
        self.robot_x, self.robot_y, self.robot_heading = robot_x, robot_y, robot_heading
        self.micro_pipe = micro_pipe
        self.axle_track = axle_track

    def goto(self, x, y):
        dx, dy = x - self.robot_x.value, y - self.robot_y.value
        magnitude = (dx * dx + dy * dy) ** .5
        d_theta = math.acos(dx / magnitude) * (-1, 1)[dy >= 0] - self.robot_heading.value
        self.micro_pipe.send((MOVEMENT, goto, (
            int(TICKS_PER_REVOLUTION * d_theta * self.axle_track / (math.pi * WHEEL_RADIUS)),
            int(TICKS_PER_REVOLUTION * magnitude / (2 * math.pi * WHEEL_RADIUS))
        )))

    def stop(self):
        self.micro_pipe.send((MOVEMENT, stop, ()))

    def move_cake(self, src, dest):
        pass

    def place_cherry(self, dest):
        pass
