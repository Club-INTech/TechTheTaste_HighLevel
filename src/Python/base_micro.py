import serial
from constants import *


class _Base:
    serial: serial.Serial
    log_level: int

    def make_message(self, id_: int, comp: int, arg: int):
        # current message scheme:
        #  | 4 bits | 4 bits |            32 bits             |
        #  |  id_   |  comp  |              arg               |
        return int.to_bytes((((id_ << 4) | comp) << 32) | arg, ORDER_LENGTH, 'big')

    def send(self, mess):
        self.serial.write(mess)

    def receive(self):
        return self.serial.read(FEEDBACK_LENGTH)

    manage_feedback = tuple(n.lower() for n in FEEDBACKS)

    def feedback(self, message):
        getattr(self, self.manage_feedback[message[0] >> 4])(message)


#  default feedback methods do nothing
BaseMicro = type('BaseMicro', (_Base,), {name: (lambda self, message: None) for name in _Base.manage_feedback})
