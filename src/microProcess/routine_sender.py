from constants import *


def goto(angle, magnitude):
    yield ROT, 0, angle + 0x10000 * (angle < 0)
    yield MOV, 0, magnitude + 0x10000 * (magnitude < 0)


def target(angle):
    yield ROT, 0, angle + 0x10000 * (angle < 0)


#control if arm is left ()
def ARMPos(leftPos, rightPos):
    yield ARM, leftPos, rightPos

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

    def goto(self, x, y, reverse=False):

        dx, dy = x - self.robot_x.value, y - self.robot_y.value
        magnitude = (dx * dx + dy * dy) ** .5
        d_theta = math.acos((1, -1)[reverse] * dx / magnitude) * (-1, 1)[dy >= 0] - self.robot_heading.value
        self.micro_pipe.send((MOVEMENT, goto, (
            int(TICKS_PER_REVOLUTION * d_theta * self.axle_track / (math.pi * WHEEL_RADIUS)),
            int(TICKS_PER_REVOLUTION * magnitude / (2 * math.pi * WHEEL_RADIUS) * (1, -1)[reverse]),
        )))

    def target(self, angle):
        d_theta = (angle - self.robot_heading.value) % (2 * math.pi)
        d_theta -= (d_theta > math.pi) * 2 * math.pi
        self.micro_pipe.send((MOVEMENT, target, (
            int(TICKS_PER_REVOLUTION * d_theta * self.axle_track / (math.pi * WHEEL_RADIUS)),
        )))
    #position = UP_arm = -1 or position = DOWN_arm  = 1
    def ARMverticalPos (self, position = UP):
        left = AmpVertiArm * position
        right = AmpVertiArm * position
        self.micro_pipe.send(ACTION, ARMPos, (left, right) )

    #position = LEFT_arm = 1 or position = RIGHT_arm = -1
    #the function onlu change of 1 step the arm so if the arm is compeletly on the left of robot, calling one time the function with 
    #args = right will put the arm on the middle of the robot
    def ARMhorizontalPos (self, position):
        left = AmpHoriArm * position
        right = (-1) * AmpHoriArm *position 
        self.micro_pipe.send(ACTION, ARMPos, (left, right) )

    def stop(self):
        self.micro_pipe.send((MOVEMENT, stop, ()))

    def move_cake(self, src, dest):
        pass

    def place_cherry(self, dest):
        pass
