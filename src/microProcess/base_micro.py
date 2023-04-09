import serial
import time
from constants import *


class BaseMicro:
    serial: serial.Serial
    log_level: int
    log_method = print

    def synchronise(self):
        self.pre_sync()
        time.sleep(1.)
        self.clear_buffer()

    def pre_sync(self):
        if self.log_level > NEC:
            self.log_method(f'{type(self).__name__}: info : Trying to sync with pico')
        self.serial.write(SYNC_BYTES)

    def clear_buffer(self):
        if self.log_level > N_NEC:
            self.log_method(f'{type(self).__name__} : info : Clearing buffer')

    def make_message(self, id_: int, comp: int, arg: int) -> bytes:
        if self.log_level > N_NEC:
            self.log_method(f'{type(self).__name__} : info : Building order with arguments {id_}({ORDERS[id_]}), {comp}, {arg}')

        # current message scheme:
        #  | 4 bits | 4 bits |            32 bits             |
        #  |  id_   |  comp  |              arg               |
        return int.to_bytes((((id_ << 4) | comp) << 32) | arg, ORDER_LENGTH, 'big')

    def send(self, mess: bytes):
        if self.log_level > NEC:
            self.log_method(f'{type(self).__name__} : info : Sending 0x{mess.hex()}')
        self.serial.write(mess)

    def receive(self) -> bytes:
        res = self.serial.read(FEEDBACK_LENGTH)
        if self.log_level > NEC:
            self.log_method(f'{type(self).__name__} : info : Received 0x{res.hex()}')
        return res

    #  default feedback methods do nothing
    def acknowledgement(self, message):
        pass

    #  default feedback methods do nothing
    def termination(self, message):
        pass

    #  default feedback methods do nothing
    def var_get(self, message):
        pass

    #  default feedback methods do nothing
    def tracked(self, message):
        pass

    #  default feedback methods do nothing
    def error(self, message):
        pass

    #  default feedback methods do nothing
    def wheel_update(self, message):
        pass

    #  default feedback methods do nothing
    def debug(self, message):
        pass

    #  default feedback methods do nothing
    def identify(self, message):
        pass

    manage_feedback = tuple(n.lower() for n in FEEDBACKS)

    def feedback(self, message):
        nb = message[0] >> 4
        if nb >= len(self.manage_feedback):
            self.log_method(f'{type(self).__name__} : ERROR : Invalid feedback received {nb}')
            return self.synchronise()
        attr = self.manage_feedback[message[0] >> 4]
        if self.log_level > N_NEC:
            self.log_method(f'{type(self).__name__} : info : Processing feedback {attr.upper()}')
        getattr(self, attr)(message)


# BaseMicro = type('BaseMicro', (_Base,), {name: (lambda self, message: None) for name in _Base.manage_feedback})
