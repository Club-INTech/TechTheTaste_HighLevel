import serial
from logger import Logger


class BaseMicro:
    ORDER_LENGTH = 5
    FEEDBACK_LENGTH = 5

    serial: serial.Serial
    log_level: int

    @Logger.log_make_message
    def make_message(self, id_: int, comp: int, arg: int):
        # current message scheme:
        #  | 4 bits | 4 bits |            32 bits             |
        #  |  id_   |  comp  |              arg               |
        return int.to_bytes((((id_ << 4) | comp) << 32) | arg, self.ORDER_LENGTH, 'big')

    @Logger.log_send
    def send(self, mess):
        self.serial.write(mess)

    @Logger.log_receive
    def receive(self):
        return self.serial.read(self.FEEDBACK_LENGTH)

    def __repr__(self):
        return 'BaseMicro'
