import serial
from multiprocessing.connection import Connection
import multiprocessing as mp
from logger import Logger
from constants import *
import sys


class MicroManager:
    ORDER_LENGTH = 3     # message length in bytes of orders
    FEEDBACK_LENGTH = 1  # message length in bytes of feedbacks

    serial: serial.Serial

    @Logger.log_make_message
    def make_message(self, id_: int, comp: int, arg: int):
        # current message scheme:
        #  | 4 bits | 4 bits |            16 bits             |
        #  |  id_   |  comp  |              arg               |
        return int.to_bytes((((id_ << 4) | comp) << 16) | arg, self.ORDER_LENGTH, 'big')

    @Logger.log_send
    def send(self, mess):
        self.serial.write(mess)

    @Logger.log_receive
    def receive(self):
        return self.serial.read(self.FEEDBACK_LENGTH)


class MicroProcces(MicroManager):
    cnt = 0

    def __repr__(self):
        return self.name

    def __init__(self, port: str, baudrate: int, main_conn: Connection, lidar_conn: Connection, name='', log_level=LOG_NECESSARY):
        self.id_ = MicroProcces.cnt
        MicroProcces.cnt += 1
        self.name = name if name else f'MicroProcess{self.id_}'
        self.log_level = log_level

        self.serial = serial.Serial(port, baudrate)

        # pipe connections
        self.main, self.lidar = main_conn, lidar_conn

        # generators for MOVEMENT orders and ACTION orders
        self.current_sequences = [iter([]), iter([])]

        self.pull(MOVEMENT)
        self.pull(ACTION)

        # start the process
        try:
            self.main_loop()
        except KeyboardInterrupt:
            pass

    @Logger.log_manage_feedback
    def manage_feedback(self, id_, order_id):
        # Nothing to do with feedback not concerning MOVEMENT or ACTION
        if TYPES[order_id] == OTHER:
            return
        if id_:  # Received terminaison
            self.next_order(TYPES[order_id])

    def next_order(self, type_):
        try:
            # Directly sends the order to the Pico
            self.send(self.make_message(*next(self.current_sequences[type_])))
        except StopIteration:
            # Asks a new order
            self.pull(type_)

    @Logger.log_pull
    def pull(self, type_):
        # Asks a new order to the main process
        self.main.send(type_)

    def _loop(self):
        # Receive data from the lidar process
        if self.lidar.poll():
            self.send(self.make_message(LIDAR, self.lidar.recv(), 0))

        # Receive data from the main process
        if self.main.poll():
            type_, gen = self.main.recv()
            self.current_sequences[type_] = gen()
            self.next_order(type_)

        # Receive feedback from the Pico
        if self.serial.in_waiting:
            feedback = self.receive()
            self.manage_feedback(feedback[0] >> 4, feedback[0] & 0xf)

    def main_loop(self):
        while True:
            self._loop()


# ----------------------------------------------- For testing purposes -------------------------------------------------

def move_square():
    for _ in range(4):
        yield FORWARDS, 1, 800
        yield ROTATE, 1, 500


def do_shit():
    yield SET_PUMPS, 0, 0x00ff
    yield MOTOR_TIME, 15, 5000


def pseudo_main(micro_conn: Connection):
    move_queue = [move_square]
    action_queue = [do_shit]

    try:
        while True:
            if micro_conn.poll():
                type_ = micro_conn.recv()
                q = (move_queue, action_queue)[type_]
                if q:
                    micro_conn.send((type_, q.pop()))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main_parent, main_child = mp.Pipe(duplex=True)
    lidar_parent, lidar_child = mp.Pipe(duplex=True)

    main = mp.Process(target=pseudo_main, args=(main_parent,))
    log_arg = LOG_NOTHING if len(sys.argv) < 3 else {'LOG_NOTHING': LOG_NOTHING, 'LOG_NECESSARY': LOG_NECESSARY, 'LOG_EVERYTHING': LOG_EVERYTHING}[sys.argv[2]]
    micro = mp.Process(target=MicroProcces, args=(sys.argv[1], 115200, main_child, lidar_child), kwargs={'log_level': log_arg})

    try:
        main.start()
        micro.start()
        main.join()
        micro.join()
    except KeyboardInterrupt:
        print("Terminated")
        main.terminate()
        micro.terminate()