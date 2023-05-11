from constants import *
from Robot import Robot
import multiprocessing as mp
import time


def goto(angle, magnitude):
    print(angle, magnitude
          )
    if angle:
        yield ROT, 0, angle + 0x10000 * (angle < 0)
    if magnitude:
        yield MOV, 0, magnitude + 0x10000 * (magnitude < 0)


def set_arm_x(dx):
    dx = dx + 0x10000 * (dx < 0)
    return ARM, 0, (dx << 16) | dx


def set_arm_y(dy):
    n_dy = -dy
    dy = dy + 0x10000 * (dy < 0)
    n_dy = n_dy + 0x10000 * (n_dy < 0)
    return ARM, 0, (n_dy << 16) | dy


def move_cake(to_src, down1, to_des, down2):
    yield set_arm_x(to_src)
    yield set_arm_y(down1)
    yield PUM, 1, 1
    time.sleep(.2)
    yield set_arm_y(-down1)
    yield set_arm_x(to_des)
    yield set_arm_y(down2)
    yield PUM, 1, 0
    yield set_arm_y(-down2)


def stop():
    yield CAN, 0, 0


def place_cherry():
    pass


class RoutineSender(Robot):

    def __init__(self, axle_track):
        Robot.__init__(self, 5)
        self.axle_track = axle_track

    def goto(self, x, y, reverse=False):
        dx, dy = x - self.x, y - self.y
        magnitude = (dx * dx + dy * dy) ** .5
        d_theta = math.acos((1, -1)[reverse] * dx / magnitude) * (-1, 1)[(dy >= 0) ^ reverse] - self.h
        self.micro_pipe.send((MOVEMENT, goto, (
            int(TICKS_PER_REVOLUTION * d_theta * self.axle_track / (4 * math.pi * WHEEL_RADIUS)),
            int(TICKS_PER_REVOLUTION * magnitude / (2 * math.pi * WHEEL_RADIUS) * (1, -1)[reverse]),
        )))

    def stop(self):
        self.micro_pipe.send((MOVEMENT, stop, ()))

    # src, destination: LEFT, MIDDLE or RIGHT (integers: 0 | 1 | 2)
    def move_cake(self, src, destination):
        to_src = HORIZONTAL_POSITIONS[src] - self.arm_x
        self.arm_x = src
        down1 = len(self.storage[src]) * CAKE_HEIGHT + LOWEST_CAKE
        to_des = HORIZONTAL_POSITIONS[destination] - self.arm_x
        self.arm_x = destination
        down2 = len(self.storage[destination]) * CAKE_HEIGHT + CAKE_HEIGHT + LOWEST_CAKE
        Robot.move_cake(self, src, destination)
        self.micro_pipe.send((ACTION, move_cake, (to_src, down1, to_des, down2)))

    def place_cherry(self, destination):
        pass


if __name__ == '__main__':
    import multiprocessing as mp
    p, truc = mp.Pipe()
    r = RoutineSender(p, AXLE_TRACK_1A)
    r.storage = ['RRR', 'JJJ', 'MMM']
    r.move_cake(0, 1)
    print(r.storage)
    print(truc.recv())
