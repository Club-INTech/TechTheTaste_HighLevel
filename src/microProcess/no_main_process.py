import time

from micro_process import MicroProcess
from constants import *
import multiprocessing as mp
from routine_sender import RoutineSender
import os, sys
import json

robot_x, robot_y, robot_h = mp.Value('f', 0.), mp.Value('f', 0.), mp.Value('f', 0.)

sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'lidarProcess'))
import lidarProcess


def lidar_process(pipe, r, color):
    lidar = lidarProcess.Lili()
    lidar.log = False
    # lidar.lidarstop(pipe)                           #simple lidar
    while True:
        continue
    #lidar.lidarstop2(pipe, r.x, r.y, r.h, start)   #with track limitation


lidar_pipe0, lidar_pipe1 = mp.Pipe()
main_pipe0, main_pipe1 = mp.Pipe()
r = RoutineSender(AXLE_TRACK_1A)
GREEN, BLUE = 0, 1


class Node:
    def tick(self, ready):
        pass

    def reset(self):
        pass


class SequenceNode(Node):

    def __init__(self, *nodes: Node):
        self.sequence: list[Node] = list(nodes)
        self.current_index = 0

    def tick(self, ready):
        if self.current_index >= len(self.sequence):
            return True
        self.current_index += self.sequence[self.current_index].tick(ready)
        return self.current_index >= len(self.sequence)

    def append(self, node: Node):
        self.sequence.append(node)
        return self

    def reset(self):
        for node in self.sequence:
            node.reset()
        self.current_index = 0


class ParallelNode(Node):
    def __init__(self, *sequences: Node):
        self.sequences = sequences

    def tick(self, ready):
        res = True
        for seq in self.sequences:
            res &= seq.tick(ready)
        return res

    def reset(self):
        for node in self.sequences:
            node.reset()


class RobotAction(Node):
    running = False

    def __init__(self, robot, type_, func_name, *args):
        self.robot, self.type_, self.func_name, self.args = robot, type_, func_name, args

    def tick(self, ready):
        if not self.running and ready[self.type_]:
            self.running = True
            ready[self.type_] = False
            getattr(self.robot, self.func_name)(*self.args)
        return ready[self.type_]

    def reset(self):
        self.running = False


class Action(Node):
    done = False

    def __init__(self, func):
        self.func = func

    def tick(self, ready):
        if not self.done:
            self.done = True
            self.func()
        return True

    def reset(self):
        self.done = False


class PartyTimer(Node):
    def __init__(self, node: Node, delay):
        self.date, self.delay, self.node = None, delay, node

    def tick(self, ready):
        if self.date is None:
            self.date = time.perf_counter()
        elapsed = time.perf_counter() - self.date
        print(f'Test Party Timer: {elapsed:.2f}/{self.delay} s ({elapsed > self.delay})', end=' ')
        return elapsed > self.delay or self.node.tick(ready)


class Timer(Node):
    def __init__(self, delay):
        self.date, self.delay = None, delay

    def tick(self, ready):
        if self.date is None:
            self.date = time.perf_counter()
        elapsed = time.perf_counter() - self.date
        print(f'Test Timer: {elapsed:.2f}/{self.delay} s ({elapsed > self.delay})', end=' ')
        return elapsed > self.delay


class JumperNode(Node):
    waiting, jumper = True, 24

    def __init__(self, edge=True):
        # edge True->front descendant, False: Front monatant

        import RPi.GPIO as GPIO  # noqa
        self.edge = (not edge, edge)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.jumper, GPIO.IN)
        self.gpio = GPIO.input

    def tick(self, ready):
        self.waiting = self.edge[self.gpio(self.jumper)]
        print(f"Waiting: {self.waiting}", end='')
        return not self.waiting


def get_tri(robot):
    with open('tri.json') as f:
        data = json.load(f)
    isomorphism = tuple(robot.storage.index(x) for x in data['start'])
    steps = (map(lambda t: isomorphism[int(t)], x.split('->')) for x in data['steps'])
    return SequenceNode(*(RobotAction(robot, ACTION, 'move_cake', *x) for x in steps))


class Scenario:
    def __init__(self, robot, pipe, node, party_time=100.):
        self.ready = [False, False]
        self.robot, self.pipe = robot, pipe
        robot.micro_pipe = pipe
        self.node: Node = SequenceNode(
            RobotAction(r, ACTION, 'set_speed', 90.),
            JumperNode(),
            PartyTimer(node, party_time), Action(lambda: print("\nFINI\n")), RobotAction(robot, MOVEMENT, 'stop'))

    def main_loop(self):
        while True:
            if self.pipe.poll():
                self.ready[self.pipe.recv()] = True
            print('\r', end='')
            self.node.tick(self.ready)
            time.sleep(.05)

    def reset(self):
        self.node.reset()

    @classmethod
    def test(cls, robot, pipe):
        return cls(robot, pipe, Timer(10.), party_time=5.)


def main_process(pipe):
    s_blue = SequenceNode()
    s_vert = SequenceNode()
    # s.append(RobotAction(r, MOVEMENT, 'goto'))

    # s.append(RobotAction(r, MOVEMENT, 'goto', .30, 0.))
    # s.append(RobotAction(r, MOVEMENT, 'goto', .60, .0))
    # s.append(RobotAction(r, MOVEMENT, 'goto', .70, -.3))
    # s.append(RobotAction(r, MOVEMENT, 'goto', 1., -.4))
    # s.append(RobotAction(r, MOVEMENT, 'goto', 1.35, -.4))
    # s.append(RobotAction(r, MOVEMENT, 'goto', 1.75, -.4))
    # s.append(RobotAction(r, MOVEMENT, 'goto', 1.75, -.1))
    # s.append(RobotAction(r, MOVEMENT, 'goto', 1.75, -.3, True))
    # s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    # s.append(RobotAction(r, MOVEMENT, 'goto', 1.3, -.25))
    # s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    # s.append(RobotAction(r, MOVEMENT, 'goto', .85, -.18))
    # s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    # s.append(RobotAction(r, MOVEMENT, 'goto', .5, -.1))
    # s.append(RobotAction(r, MOVEMENT, 'goto', .1, -.05))

    # ParallelNode(RobotAction(r, MOVEMENT, 'goto', 0.4, 0), RobotAction(r, ACTION, 'move_arm', 3000, 3000))

    # s.append(Action(lambda: print('Position', r.x, r.y, r.h)))
    # s.append(Action(r, MOVEMENT, 'goto', .4, 0.))

    # w1 = TestWaiter(5.)
    # w2 = TestWaiter(15.)
    #
    # p = ParallelNode(w1, w2)
    # s = SequenceNode()
    # s.append(p)
    # s.append(Action(lambda: print('\nFinished')))

    # sc = Scenario(r, pipe, s)
    # sc = Scenario(r, pipe, RobotAction(r, ACTION, 'move_cake', LEFT, RIGHT))

    sc_bleu = Scenario(r, pipe, s_blue
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'rotate', math.pi / 8))
        .append(RobotAction(r, MOVEMENT, 'goto', .3, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .3, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .3, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .3, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'rotate', -math.pi / 10))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .1, 0.))
        .append(Action(lambda: setattr(r, 'storage', ['MMM', 'RRR', 'JJJ'])))
        .append(get_tri(r))
    )
    # sc = Scenario.test(r, pipe)

    sc_vert = Scenario(r, pipe, s_vert
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'rotate', -math.pi / 8))
        .append(RobotAction(r, MOVEMENT, 'goto', .3, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .3, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .3, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .3, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'rotate', math.pi / 10))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .2, 0.))
        .append(RobotAction(r, MOVEMENT, 'goto', .1, 0.))
    )

    sc_bleu.main_loop()
    # sc_vert.main_loop()


if __name__ == '__main__':
    color = GREEN
    
    main_ = mp.Process(target=main_process, args=(main_pipe0,))
    lidar_ = mp.Process(target=lidar_process, args=(lidar_pipe1, r, color))
    micro_ = mp.Process(target=MicroProcess, args=(lidar_pipe0, main_pipe1, r, False))

    lidar_.start()
    main_.start()
    micro_.start()

    try:
        micro_.join()
    except KeyboardInterrupt:
        lidar_.terminate()
        main_.terminate()
        micro_.terminate()
    # print(r.x, r.y)
