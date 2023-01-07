from base_micro import *
from constants import *

import multiprocessing as mp
import random as rd
import time
import sys


class MicroProc(BaseMicro):
    def __init__(self, port, baudrate, lidar, main, log=NECESSARY):
        self.serial = serial.Serial(port, baudrate)
        self.log_level = log

        self.lidar, self.main = lidar, main
        self.sequences = [iter([]), iter([])]

    @Logger.log_next
    def next(self, type_):
        try:
            next_order = next(self.sequences[type_])
            self.send(self.make_message(*next_order))
            if next_order[0] == MOTS:
                for _ in range(next_order[1]):
                    self.send(self.make_message(*next_order))
        except StopIteration:
            self.pull(type_)

    @Logger.log_manage_feedback
    def manage_feedback(self, id_, order_id):
        type_ = TYPES[order_id]
        if type_ == OTHER:
            return
        elif id_:
            self.next(type_)

    @Logger.log_pull
    def pull(self, type_):
        self.main.send(type_)

    def _loop(self):
        if self.lidar.poll():
            self.send(self.make_message(LID, self.lidar.recv(), 0))
        if self.main.poll():
            type_, gen = self.main.recv()
            self.sequences[type_] = gen()
            self.next(type_)
        if self.serial.in_waiting:
            feedback = self.receive()
            self.manage_feedback(feedback[0] >> 4, feedback[0] & 0xf)

    def mainloop(self):
        try:
            self.pull(ACTION)
            self.pull(MOVEMENT)
            while True:
                self._loop()
        except KeyboardInterrupt:
            self.send(self.make_message(CAN, 0, 0))


main_conn1, main_conn2 = mp.Pipe()
lidar_conn1, lidar_conn2 = mp.Pipe()


def verify_neg(v):
    return v + (v < 0) * 0x10000


def action():
    yield MOTS, 5, 0b0010011000010001
    yield MOTS_A, 0, rd.randrange(MIN_T_MS, MAX_T_MS)
    yield MOTS_A, 4, rd.randrange(MIN_T_MS, MAX_T_MS)
    yield MOTS_A, 9, rd.randrange(MIN_T_MS, MAX_T_MS)
    yield MOTS_A, 10, rd.randrange(MIN_T_MS, MAX_T_MS)
    yield MOTS_A, 13, rd.randrange(MIN_T_MS, MAX_T_MS)

    yield PUM, 0, 0b0000001111000011

    yield MOT_VALUE, 2, 500
    yield MOT_TIME, 15, rd.randrange(MIN_T_MS, MAX_T_MS)

    yield PUM, 0, 0


def move():
    yield CAN, 0, 0
    for _ in range(8):
        yield MOV, 0, verify_neg(rd.randrange(MIN_TICKS, MAX_TICKS))
        yield ROT, 0, verify_neg(rd.randrange(MIN_TICKS, MAX_TICKS))


def main_process(pipe):
    try:
        while True:
            value = pipe.recv()
            pipe.send(((MOVEMENT, move), (ACTION, action))[value])
    except KeyboardInterrupt:
        pass


def lidar_process(pipe):
    try:
        while True:
            time.sleep(5)
            pipe.send(1)
            time.sleep(1.2)
            pipe.send(0)
            time.sleep(15)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main = mp.Process(target=main_process, args=(main_conn1,))
    lidar = mp.Process(target=lidar_process, args=(lidar_conn1,))

    port = sys.argv[1]
    log = NECESSARY if len(sys.argv) < 3 else LOG_MODES.index(sys.argv[2])

    try:
        main.start()
        lidar.start()
        MicroProc(port, 115200, lidar_conn2, main_conn2, log).mainloop()
    except KeyboardInterrupt:
        main.terminate()
        lidar.terminate()

