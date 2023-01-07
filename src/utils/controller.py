import struct
from multiprocessing import Process, SimpleQueue

EVENT_TYPES = ('OTHER', 'DIGITAL', 'ANALOG', 'PAD')

DIGITAL_BUTTONS = (
    'x', 'o', 'Δ', '□', 'L1', 'R1', 'L2', 'R2', 'Share', 'Options', 'Playstation', 'L3', 'R3'
)

ANALOG_BUTTONS = (
    'Lx', 'Ly', 'L2', 'Rx', 'Ry', 'R2', 'H_arrows', 'V_arrows'
)

PAD_STATES = (
    'FREE', 'CLICKED'
)

BUTTONS = (
    type('', (), {'__getitem__': lambda self, it: ''})(), DIGITAL_BUTTONS, ANALOG_BUTTONS, PAD_STATES
)


class Event:
    __slots__ = 'b_id', 'b_type', 'value'

    def __init__(self, b_id, b_type, value):
        self.b_id, self.b_type, self.value = b_id, 0 if b_type < 0 else b_type, value

    def __repr__(self):
        return f'Event<type={EVENT_TYPES[self.b_type]}, button={BUTTONS[self.b_type][self.b_id]}, value={self.value}'


class Controller:
    event_format = '3Bh2b'
    event_length = struct.calcsize(event_format)

    def __init__(self, queue, location='/dev/input/js0'):
        self.file, self.queue = location, queue

    def mainloop(self):
        try:
            with open(self.file, 'rb') as f:
                while True:
                    self.queue.put(Event(*struct.unpack(self.event_format, f.read(self.event_length))[:2:-1]))
        except KeyboardInterrupt:
            print('Terminated Controller Process')


class ControllerMouse:
    event_length = 3

    def __init__(self, queue, location='/dev/input/mouse0'):
        self.file, self.queue = location, queue
        self.pad_state = 0

    def mainloop(self):
        try:
            with open(self.file, 'rb') as f:
                while True:
                    h, dx, dy = f.read(self.event_length)
                    if (h & 1) ^ self.pad_state:
                        self.pad_state = h & 1
                        self.queue.put(Event(h & 1, 3, None))
                    self.queue.put(Event(h & 1, 3, ((dx - 256 if dx > 128 else dx), dy - 256 if dy > 128 else dy)))
        except KeyboardInterrupt:
            print('Terminated Mouse Process')


Q = SimpleQueue()


def get(num=None):
    if num is None:
        while not Q.empty():
            yield Q.get()
    else:
        for i in range(num):
            if not Q.empty():
                r = Q.get()
                if Q.empty():
                    return r
                yield Q.get()


(p  := Process(target=Controller(Q).mainloop)).start()
(p_ := Process(target=ControllerMouse(Q).mainloop)).start()

if __name__ == '__main__':
    import time
    try:
        while True:
            print('Pulling events')
            for ev in get():
                print(ev)
            time.sleep(.5)
    except KeyboardInterrupt:
        print('Terminated')