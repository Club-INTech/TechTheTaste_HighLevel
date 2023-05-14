from micro_process import MicroProcess
from constants import *
import multiprocessing as mp
from routine_sender import RoutineSender
import os, sys

robot_x, robot_y, robot_h = mp.Value('f', 0.), mp.Value('f', 0.), mp.Value('f', 0.)

sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'lidarProcess'))
import lidarProcess


def lidar_process(pipe, r, color):
    lidar = lidarProcess.Lili()
    lidar.log = False
    lidar.lidarstop(pipe)                           #simple lidar
    #lidar.lidarstop2(pipe, r.x, r.y, r.h, start)   #with track limitation


lidar_pipe0, lidar_pipe1 = mp.Pipe()
main_pipe0, main_pipe1 = mp.Pipe()
r = RoutineSender(AXLE_TRACK_1A)
GREEN, BLUE = 0, 1


class Node:
    def tick(self, ready):
        pass


class SequenceNode(Node):
    def __init__(self):
        self.sequence: list[Node] = []
        self.current_index = 0

    def tick(self, ready):
        if self.current_index >= len(self.sequence):
            return True
        self.current_index += self.sequence[self.current_index].tick(ready)
        return self.current_index >= len(self.sequence)

    def append(self, node: Node):
        self.sequence.append(node)


class ParallelNode(Node):
    def __init__(self, *sequences: SequenceNode):
        self.sequences = sequences

    def tick(self, ready):
        res = False
        for seq in self.sequences:
            res &= seq.tick(ready)
        return res


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


class Action(Node):
    done = False

    def __init__(self, func):
        self.func = func

    def tick(self, ready):
        if not self.done:
            self.done = True
            self.func()
        return True


class Scenario:
    def __init__(self, robot, pipe, node):
        self.ready = [False, False]
        self.robot, self.pipe = robot, pipe
        robot.micro_pipe = pipe
        self.node: Node = node

    def main_loop(self):
        while True:
            if self.pipe.poll():
                self.ready[self.pipe.recv()] = True
            self.node.tick(self.ready)


def main_process(pipe):
    r.storage = ['R', '', '']
    s = SequenceNode()
    s.append(RobotAction(r, MOVEMENT, 'goto', .4, 0.))
    s.append(Action(lambda: print(r.x, r.y)))
    # s.append(Action(r, MOVEMENT, 'goto', .4, 0.))
    sc = Scenario(r, pipe, s)
    sc.main_loop()


if __name__ == '__main__':
    color = GREEN
    
    main_ = mp.Process(target=main_process, args=(main_pipe0,))
    lidar_ = mp.Process(target=lidar_process, args=(lidar_pipe1, r, color))
    micro_ = mp.Process(target=MicroProcess, args=(lidar_pipe0, main_pipe1, r, True))

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
