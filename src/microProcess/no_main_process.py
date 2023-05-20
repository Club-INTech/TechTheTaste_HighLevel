import time

from micro_process import MicroProcess
from constants import *
import multiprocessing as mp
from routine_sender import RoutineSender
import os
import sys
import json

robot_x, robot_y, robot_h = mp.Value('f', 0.), mp.Value('f', 0.), mp.Value('f', 0.)

sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'lidarProcess'))
import lidarProcess


def lidar_process(pipe, r, color):
    lidar = lidarProcess.Lili()
    lidar.log = True
    lidar.lidar_stop3(pipe)

    # while True:
    #     continue
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

    def symetry(self):
        return Node()


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

    def symetry(self):
        return SequenceNode(*(n.symetry() for n in self.sequence))


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

    def symetry(self):
        return ParallelNode(*(n.symetry() for n in self.sequences))


class RobotAction(Node):
    running = False

    def __init__(self, robot, type_, func_name, *args):
        self.robot, self.type_, self.func_name, self.args = robot, type_, func_name, args

    def tick(self, ready):
        print(self.func_name, ' ', end='')
        if not self.running and ready[self.type_]:
            self.running = True
            ready[self.type_] = False
            getattr(self.robot, self.func_name)(*self.args)
        return ready[self.type_]

    def reset(self):
        self.running = False

    def _goto(self):
        return (self.args[0], -self.args[1]) + self.args[2:]

    def _rotate(self):
        return -self.args[0],

    def _move_cake(self):
        return (2 - a for a in self.args)

    managed = 'goto', 'rotate', 'move_cake'

    def symetry(self):
        sym_args = getattr(self, f'_{self.func_name}')() if self.func_name in self.managed else self.args
        return RobotAction(self.robot, self.type_, self.func_name, *sym_args)


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

    def symetry(self):
        return Action(self.func)


class PartyTimer(Node):
    def __init__(self, node: Node, delay):
        self.date, self.delay, self.node = None, delay, node

    def tick(self, ready):
        if self.date is None:
            self.date = time.perf_counter()
        elapsed = time.perf_counter() - self.date
        print(f'Test Party Timer: {elapsed:.2f}/{self.delay} s ({elapsed > self.delay})', end=' ')
        return elapsed > self.delay or self.node.tick(ready)

    def symetry(self):
        return PartyTimer(self.node.symetry(), self.delay)


class Timer(Node):
    def __init__(self, delay):
        self.date, self.delay = None, delay

    def tick(self, ready):
        if self.date is None:
            self.date = time.perf_counter()
        elapsed = time.perf_counter() - self.date
        print(f'Test Timer: {elapsed:.2f}/{self.delay} s ({elapsed > self.delay})', end=' ')
        return elapsed > self.delay

    def symetry(self):
        return Timer(self.delay)


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
        # print(f"Waiting: {self.waiting}", end='')
        return not self.waiting

    def symetry(self):
        return JumperNode(self.edge[1])


def get_tri(robot, storage):
    with open('tri.json') as f:
        data = json.load(f)
    isomorphism = tuple(storage.index(x) for x in data['start'])
    steps = (map(lambda t: isomorphism[int(t)], x.split('->')) for x in data['steps'])
    return SequenceNode(*(RobotAction(robot, ACTION, 'move_cake', *x) for x in steps))


class Scenario:
    def __init__(self, robot, pipe, node, party_time=100.):
        self.ready = [False, False]
        self.robot, self.pipe, self.party_time = robot, pipe, party_time
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

    def symetry(self):
        return Scenario(self.robot, self.pipe, self.node.symetry(), self.party_time)


def main_process(pipe):

    sc_bleu = Scenario(r, pipe, SequenceNode(
        Action(lambda: setattr(r, 'timeout_delay', 1.5)),
        RobotAction(r, MOVEMENT, 'goto', .2, 0.),
        RobotAction(r, MOVEMENT, 'rotate', math.pi / 8),
        RobotAction(r, MOVEMENT, 'goto', .3, 0.),
        RobotAction(r, MOVEMENT, 'goto', .3, 0.),
        RobotAction(r, MOVEMENT, 'goto', .3, 0.),
        RobotAction(r, MOVEMENT, 'goto', .3, 0.),
        RobotAction(r, MOVEMENT, 'goto', .1, 0.),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 7),
        RobotAction(r, MOVEMENT, 'goto', .3, 0.),
        RobotAction(r, MOVEMENT, 'goto', .3, 0.),
        RobotAction(r, MOVEMENT, 'goto', .2, 0.),
        RobotAction(r, MOVEMENT, 'goto', .2, 0.),
        Action(lambda: setattr(r, 'storage', ['MMM', 'RRR', 'JJJ'])),
        PartyTimer(get_tri(r, ['MMM', 'RRR', 'JJJ']), 60.),
        RobotAction(r, MOVEMENT, 'goto', -.08, 0., True),
        RobotAction(r, MOVEMENT, 'goto', -.08, 0., True),
        RobotAction(r, MOVEMENT, 'goto', -.08, 0., True),
        RobotAction(r, MOVEMENT, 'goto', -.08, 0., True),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'goto', .2, 0.),
        RobotAction(r, MOVEMENT, 'goto', .2, 0.),
        RobotAction(r, MOVEMENT, 'goto', .1, 0.)
    ))
    # sc = Scenario.test(r, pipe)

    sc_vert = sc_bleu.symetry()

    sc_panik = Scenario(r, pipe, SequenceNode(
        Action(lambda: setattr(r, 'timeout_delay', 1.5)),
        RobotAction(r, MOVEMENT, 'goto', .4, 0.),
        RobotAction(r, MOVEMENT, 'goto', -.4, 0., True)
    ))

    sc_test = Scenario(r, pipe, SequenceNode(
        Action(lambda: setattr(r, 'timeout_delay', 1.5)),
        RobotAction(r, MOVEMENT, 'goto', .2, 0.),
        RobotAction(r, MOVEMENT, 'goto', .2, 0.),
        RobotAction(r, MOVEMENT, 'rotate', math.pi / 8),
        RobotAction(r, MOVEMENT, 'goto', .2, 0.),
        RobotAction(r, MOVEMENT, 'rotate', math.pi / 9),
        # Action(lambda: setattr(r, 'timeout_delay', .5)),
        *(RobotAction(r, MOVEMENT, 'goto', .2, 0.) for _ in range(12)),
        Action(lambda: setattr(r, 'timeout_delay', 1.5)),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 8),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 8),
        RobotAction(r, MOVEMENT, 'goto', .2, 0.),
        RobotAction(r, MOVEMENT, 'goto', -.2, 0., True),
        RobotAction(r, MOVEMENT, 'goto', -.2, 0., True),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 5),
        *(RobotAction(r, MOVEMENT, 'goto', .2, 0.) for _ in range(5)),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 8),
        *(RobotAction(r, MOVEMENT, 'goto', .2, 0.) for _ in range(3)),
        Action(lambda: setattr(lidarProcess.dmin, 'value', 250)),
        *(RobotAction(r, MOVEMENT, 'goto', .06, 0.) for _ in range(4)),
    ))

    sc_test2 = Scenario(r, pipe, SequenceNode(
        Action(lambda: setattr(r, 'timeout_delay', 1.5)),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        RobotAction(r, MOVEMENT, 'rotate', -math.pi / 6),
        *(RobotAction(r, MOVEMENT, 'goto', .2, 0.) for _ in range(8)),
    ))

    print('Main Process')

    scenarios = {
        'vert': sc_vert,
        'panik': sc_panik,
        'bleu': sc_bleu,
        'test': sc_test,
        'test2': sc_test2
    }
    scenarios[sys.argv[1]].main_loop()
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
