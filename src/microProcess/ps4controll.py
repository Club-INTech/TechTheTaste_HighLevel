import sys
from controller import Controller
from controller.constants import *
from base_micro import *
import serial
import time


class PS4Control1A(MicroManager):
    log_level = DEBUG

    def __init__(self):
        self.controller = Controller()
        self.controller.start()

        MicroManager.__init__(self)

        self.h_speed, self.v_speed = 0, 0
        self.left_target, self.right_target = 0, 0

    def send(self, port, id_, comp, arg):
        if port not in self.serials:
            return print(f'{BOARDS[port]} is not connected')
        usb = self.serials[port]
        usb.send(usb.make_message(id_, comp, arg))
        return True

    def nothing(self, event):
        pass

    def cross(self, event):
        # catch cake
        if event.value:
            print('Catching the cake')

    def circle(self, event):
        # drop cake
        if event.value:
            print('Dropping the cake')

    def triangle(self, event):
        # place cherry
        if event.value:
            print('Placing a cherry')

    def ly(self, event):
        # move
        self.v_speed = -event.value
        # print(f"Movement speed {event.value}")

    def rx(self, event):
        # rotate
        self.h_speed = -event.value
        # print(f"Rotatating speed {event.value}")

    def h_arrows(self, event):
        # horizontal deplacement of the kart
        self.left_target = self.right_target = -100 if event.value < 0 else 100 if event.value > 0 else 0

    def v_arrows(self, event):
        # vertical displacement of the kart
        self.right_target = -50 if event.value < 0 else 50 if event.value > 0 else 0
        self.left_target = -self.right_target

    manage_event = {
        (DIGITAL, CROSS): 'cross',
        (DIGITAL, CIRCLE): 'circle',
        (DIGITAL, TRIANGLE): 'triangle',
        (ANALOG, LY): 'ly',
        (ANALOG, RX): 'rx',
        (ANALOG, H_ARROWS): 'h_arrows',
        (ANALOG, V_ARROWS): 'v_arrows'
    }

    def mainloop(self):
        step = False
        while True:
            self.send(PICO1, CAN, 0, 0)
            date = time.perf_counter()
            # little movement either rotation or translation
            value = (self.h_speed, self.v_speed)[step] // 8
            if value:
                self.send(PICO1, (ROT, MOV)[step], 0, value + 0x10000 * (value < 0))
            step ^= True
            left, right = self.left_target + 0x10000 * (self.left_target < 0), self.right_target + 0x10000 * (self.right_target < 0)
            self.send(PICO2, ARM, 0, (left << 16) | right)
            # delays for 20 ms
            while time.perf_counter() - date < .02:
                for event in self.controller.get_events():
                    # gets the method corresponding to the event, if the event is not managed, it does nothing
                    getattr(self, self.manage_event.get((event.type, event.button), 'nothing'))(event)
                self.scan_feedbacks()


if __name__ == '__main__':
    p = PS4Control1A()
    try:
        p.mainloop()
    except KeyboardInterrupt:
        p.controller.terminate()
        print()
