import time

from constants import *


def goto(angle, magnitude):
    yield TRACK, 0, 0
    yield ROT, 0, angle + 0x10000 * (angle < 0)
    while abs(magnitude) > 2000:
        if magnitude > 0:
            yield MOV, 0, 2000
            magnitude -= 2000
        else:
            yield MOV, 0, -2000 + 0x10000
            magnitude += 2000
    yield MOV, 0, magnitude + 0x10000 * (magnitude < 0)
    yield TRACK, 0, 0


def target(angle):
    yield TRACK, 0, 0
    yield ROT, 0, angle + 0x10000 * (angle < 0)
    yield TRACK, 0, 0


def set_arm_x(dx):
    dx = dx + 0x10000 * (dx < 0)
    return ARM, 0, (dx << 16) | dx


def set_arm_y(dy):
    n_dy = -dy
    dy = dy + 0x10000 * (dy < 0)
    n_dy = -n_dy + 0x10000 * (n_dy < 0)
    return ARM, 0, (dy << 16) | n_dy


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


#PUMPstate is a bytemask to controll all the pump on the bot
#for instance if you want to turn on only pump1, call pumpState(0b00000001)
#Actuator2A is a bytemask tocontroll all the actuator of the bot
#ValveState is a bytemask to controll all the valve of the bot
#use the order pump https://docs.google.com/spreadsheets/d/1NDprMKYs9L7S2TkqgACDOh6OKDJRHhz_LrTCKmEuD-k/edit#gid=0

def actuatorControll(PUMPstate : int, Actuator2A : int, ValveState : int):
    yield PUM, 7, (ValveState << 16) | (Actuator2A << 8) | (PUMPstate)


def stop():
    yield CAN, 0, 0


def place_cherry():
    pass


class RoutineSender:

    def __init__(self, robot_x, robot_y, robot_heading, arm_pos_x, rake_state, micro_pipe, axle_track):
        self.rake_state = rake_state
        self.robot_x, self.robot_y, self.robot_heading, self.arm_pos_x = robot_x, robot_y, robot_heading, arm_pos_x
        self.micro_pipe = micro_pipe
        self.axle_track = axle_track

    def goto(self, x, y, reverse=False):
        dx, dy = x - self.robot_x.value, y - self.robot_y.value
        magnitude = (dx * dx + dy * dy) ** .5
        d_theta = math.acos((1, -1)[reverse] * dx / magnitude) * (-1, 1)[(dy >= 0) ^ reverse] - self.robot_heading.value
        self.micro_pipe.send((MOVEMENT, goto, (
            int(TICKS_PER_REVOLUTION * d_theta * self.axle_track / (4 * math.pi * WHEEL_RADIUS)),
            int(TICKS_PER_REVOLUTION * magnitude / (2 * math.pi * WHEEL_RADIUS) * (1, -1)[reverse]),
        )))

    def target(self, angle):
        d_theta = (angle - self.robot_heading.value) % (2 * math.pi)
        d_theta -= (d_theta > math.pi) * 2 * math.pi
        self.micro_pipe.send((MOVEMENT, target, (
            int(TICKS_PER_REVOLUTION * d_theta * self.axle_track / (math.pi * WHEEL_RADIUS)),
        )))

    #position = UP_arm = -1 or position = DOWN_arm  = 1
    UP_arm, DOWN_arm = -1, 1
    def ARMverticalPos (self, position = UP_arm):
        left = AmpVertiArm * position
        right = AmpVertiArm * position
        self.micro_pipe.send(ACTION, ARMPos, (left, right) )

    # pos: LEFT, MIDDLE, or RIGHT
    def set_arm_x(self, pos):
        self.micro_pipe.send(ACTION, set_arm_x, (pos - self.arm_pos_x.value,))
        self.arm_pos_x = pos

    # pos: DOWN, UP
    def set_arm_y(self, pos):
        down_pos = len(self.rake_state[X_POSITIONS.index(self.arm_pos_x.value)]) * CAKE_HEIGHT + ONE_CAKE
        destination = (down_pos, 0)[pos]
        self.micro_pipe.send(ACTION, set_arm_y, (destination - self.arm_pos_y.value,))
        self.arm_pos_y = destination

    def PumpControll(self, byteMask):
        self.micro_pipe.send(ACTION, actuatorControll, (byteMask, 0, 0) )

    def Actuator2AControll(self, byteMask):
        self.micro_pipe.send(ACTION,actuatorControll, (0, byteMask, 0))

    def ValveControll(self, byteMask):
        self.micro_pipe.send(ACTION, actuatorControll, (0, 0, byteMask))

    def stop(self):
        self.micro_pipe.send((MOVEMENT, stop, ()))

    # src, destination: LEFT, MIDDLE or RIGHT
    def move_cake(self, src, destination):
        to_src = src - self.arm_pos_x.value
        self.arm_pos_x.value = src
        down1 = len(self.rake_state[X_POSITIONS.index(self.arm_pos_x.value)]) * CAKE_HEIGHT + ONE_CAKE
        to_des = destination - self.arm_pos_x.value
        self.arm_pos_x.value = destination
        down2 = len(self.rake_state[X_POSITIONS.index(self.arm_pos_x.value)]) * CAKE_HEIGHT + CAKE_HEIGHT + ONE_CAKE
        self.micro_pipe.send(ACTION, move_cake, (to_src, down1, to_des, down2))

    def place_cherry(self, dest):
        pass
