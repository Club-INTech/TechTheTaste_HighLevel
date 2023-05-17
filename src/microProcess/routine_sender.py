from constants import *
from multiprocessing import Value
import time


def goto(angle, magnitude):
    print(angle, magnitude
          )
    if angle:
        yield ROT, 0, angle + 0x10000 * (angle < 0)
    if magnitude:
        yield MOV, 0, magnitude + 0x10000 * (magnitude < 0)

def rot(angle):
    yield ROT, 0, angle + 0x10000 * (angle < 0)


def move(mag):
    yield MOV, 0, mag + 0x10000 * (mag < 0)


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
    yield set_arm_y(-down1)
    yield set_arm_x(to_des)
    yield set_arm_y(down2)
    yield PUM, 1, 0
    yield set_arm_y(-down2)


def stop():
    yield CAN, 0, 0


def place_cherry():
    pass


class Robot:

    def __init__(self, slot_size, axle_track):
        self.micro_pie = None
        self.slot_size = slot_size
        self.storage = ['', '', '']
        self._x, self._y, self._h, self.arm_x = Value('f'), Value('f'), Value('f'), 0
        self.axle_track = axle_track

    x = property((lambda self: self._x.value), (lambda self, value: setattr(self._x, 'value', value)))
    y = property((lambda self: self._y.value), (lambda self, value: setattr(self._y, 'value', value)))
    h = property((lambda self: self._h.value), (lambda self, value: setattr(self._h, 'value', value)))

    def move_cake(self, src, destination):
        cake = self.storage[src][-1]
        self.storage[src] = self.storage[src][:-1]
        self.storage[destination] += cake


class RoutineSender(Robot):
    micro_pipe = None

    def __init__(self, axle_track):
        Robot.__init__(self, 5, axle_track)

    def goto(self, x, y, reverse=False):
        dx, dy = x - self.x, y - self.y
        print('Goto: difference vector', dx, dy)
        magnitude = (dx * dx + dy * dy) ** .5
        d_theta = ((math.acos((1, -1)[reverse] * dx / magnitude) * (-1, 1)[(dy >= 0) ^ reverse] - self.h + math.pi) % (2 * math.pi)) - math.pi
        print(f'D theta = {d_theta / math.pi * 180}')
        self.micro_pipe.send((MOVEMENT, goto, (
            int(-TICKS_PER_REVOLUTION * d_theta * self.axle_track / (4 * math.pi * WHEEL_RADIUS)),
            int(TICKS_PER_REVOLUTION * magnitude / (2 * math.pi * WHEEL_RADIUS) * (1, -1)[reverse]),
        )))

    def move(self, mag):
        self.micro_pipe.send((MOVEMENT, move, int(TICKS_PER_REVOLUTION * mag / (2 * math.pi * WHEEL_RADIUS))))

    def rotate(self, angle):
        self.micro_pipe.send((MOVEMENT, rot, int(-TICKS_PER_REVOLUTION * angle * self.axle_track / (4 * math.pi * WHEEL_RADIUS))))

    def stop(self):
        self.micro_pipe.send((MOVEMENT, stop, ()))

    # src, destination: LEFT, MIDDLE or RIGHT (integers: 0 | 1 | 2)
    def move_cake(self, src, destination):
        # go to the source slot to grab the cake
        to_src = HORIZONTAL_POSITIONS[src] - self.arm_x
        self.arm_x = HORIZONTAL_POSITIONS[src]

        # go down to grab the cake and back up
        down1 = len(self.storage[src]) * CAKE_HEIGHT + LOWEST_CAKE

        # go to the destination slot to release the cake
        to_des = HORIZONTAL_POSITIONS[destination] - self.arm_x
        self.arm_x = HORIZONTAL_POSITIONS[destination]

        # go down to release the cake and back up
        down2 = len(self.storage[destination]) * CAKE_HEIGHT + CAKE_HEIGHT + LOWEST_CAKE
        Robot.move_cake(self, src, destination)
        self.micro_pipe.send((ACTION, move_cake, (to_src, down1, to_des, down2)))

    def place_cherry(self, destination):
        pass


if __name__ == '__main__':
    import multiprocessing as mp
    p, truc = mp.Pipe()
    r = RoutineSender(AXLE_TRACK_1A)
    r.micro_pipe = p
    r.storage = ['RRR', 'JJJ', 'MMM']
    r.move_cake(0, 1)
    print(r.storage)
    print(truc.recv())
