import serial
from serial.tools.list_ports import comports
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
        if self.log_level > NECESSARY:
            self.log_method(f'{type(self).__name__}: info : Trying to sync with hardware {self}')
        self.serial.write(SYNC_BYTES)

    def clear_buffer(self):
        if self.log_level > NOT_NECESSARY:
            self.log_method(f'{type(self).__name__} : info : Clearing buffer')
        self.serial.read(self.serial.in_waiting)

    def make_message(self, id_: int, comp: int, arg: int) -> bytes:
        if self.log_level > NOT_NECESSARY:
            self.log_method(f'{type(self).__name__} : info : Building order with arguments {id_}({ORDERS[id_]}), {comp}, {arg}')

        # current message scheme:
        #  | 4 bits | 4 bits |            32 bits             |
        #  |  id_   |  comp  |              arg               |
        return int.to_bytes((((id_ << 4) | comp) << 32) | arg, ORDER_LENGTH, 'big')

    def send(self, mess: bytes):
        if self.log_level > NECESSARY:
            self.log_method(f'{type(self).__name__} : info : Sending 0x{mess.hex()}')
        self.serial.write(mess)

    def receive(self) -> bytes:
        res = self.serial.read(FEEDBACK_LENGTH)
        if self.log_level > NECESSARY:
            self.log_method(f'{type(self).__name__} : info : Received 0x{res.hex()}')
        return res

    def manage_error(self):
        pass

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
            self.manage_error()
            print('hey')
            return self.synchronise()
        attr = self.manage_feedback[message[0] >> 4]
        if self.log_level > NOT_NECESSARY:
            self.log_method(f'{type(self).__name__} : info : Processing feedback {attr.upper()}')
        getattr(self, attr)(message)


class GenericMicro(BaseMicro):
    id_ = -1

    def __init__(self, serial_, master):
        self.master = master
        self.serial = serial_

    @classmethod
    def new(cls, old):
        return cls(old.serial, old.master)

    @property
    def log_level(self):
        return self.master.log_level

    @property
    def log_method(self):
        return self.master.log_method

    def identify(self, message):
        self.id_ = message[0] & 0xf

    def __repr__(self):
        return f'{type(self).__name__} on {self.serial.portstr}'


class MovementMicro(GenericMicro):
    id_ = 0


class ActionMicro(GenericMicro):
    id_ = 1


class ArduinoMicro(GenericMicro):
    id_ = 2


DEFAULT_MICRO_CLASSES = MovementMicro, ActionMicro, ArduinoMicro


class MicroManager:
    micro_classes = DEFAULT_MICRO_CLASSES

    log_method = print
    log_level = MINIMAL

    def __init__(self):
        serials = tuple(
            GenericMicro(serial.Serial(usb.device, BAUDRATE), self) for usb in comports() if 'COM' in usb.device or 'USB' in usb.device
        )

        for s in serials:
            s.pre_sync()
        time.sleep(1.)
        for index, s in enumerate(serials):
            s.clear_buffer()
            s.send(s.make_message(ID, 0, 0))

        # identifies all serial connections
        # any port that is not responding within 5 secs will be discarded
        date = time.perf_counter()
        while any(s.id_ == -1 for s in serials) and time.perf_counter() - date < 5.:
            for s in serials:
                if s.serial.in_waiting:
                    s.feedback(s.receive())

        for s in serials:
            if s.id_ != -1 or self.log_level <= NECESSARY:
                continue
            self.log_method(f'{type(self).__name__} : info : Could not identify hardware on {s.serial.portstr}')

        self.serials = {
            s.id_: self.micro_classes[s.id_].new(s) for s in serials if s.id_ != -1
        }

    def scan_feedbacks(self):
        for s in self.serials.values():
            if s.serial.in_waiting:
                s.feedback(s.receive())
