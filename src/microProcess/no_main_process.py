from micro_process import MicroProcess
from constants import *
import multiprocessing as mp
import sys
import time

robot_x, robot_y, robot_h = mp.Value('f', 0.), mp.Value('f', 0.), mp.Value('f', 0.)


def lidar_process():
    while True:
        continue


def move():
    yield MOV, 0, 2000
    yield ROT, 0, 200
    yield ROT, 0, -200 + 0x10000
    yield MOV, 0, -2000 + 0x10000


def vert(dv):
    n_dv = -dv
    dv += 0x10000 * (dv < 0)
    n_dv += 0x10000 * (n_dv < 0)
    return ARM, 0, (n_dv << 16) | dv


def horiz(dh):
    dh += 0x10000 * (dh < 0)
    print(dh)
    return ARM, 0, (dh << 16) | dh


def arm():
    yield horiz(-700)
    yield vert(-600)
    yield PUM, 1, 1
    time.sleep(0.1)
    yield vert(600)
    yield horiz(-700)
    yield vert(-600)
    yield PUM, 1, 0
    yield vert(600)
    yield horiz(1400)


def main_process(pipe):
    while True:
        if pipe.poll():
            x = pipe.recv()
            if not x:
                 pipe.send((0, move, ()))
            # if x:
            #     pipe.send((1, arm, ()))
            #     break
    while True:
        continue


lidar_pipe, _ = mp.Pipe()
main_pipe0, main_pipe1 = mp.Pipe()


if __name__ == '__main__':
    main_ = mp.Process(target=main_process, args=(main_pipe0,))
    lidar_ = mp.Process(target=lidar_process, args=())
    micro_ = mp.Process(target=MicroProcess, args=(sys.argv[1], lidar_pipe, main_pipe1, robot_x, robot_y, robot_h, 1., DEBUG))

    lidar_.start()
    main_.start()
    micro_.start()

    try:
        micro_.join()
    except KeyboardInterrupt:
        lidar_.terminate()
        main_.terminate()
        micro_.terminate()

