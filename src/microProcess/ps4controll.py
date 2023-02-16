from controller import Controller
from controller.constants import *
from base_micro import BaseMicro
from constants import *
import serial
import time


class PS4Controll1A(BaseMicro):
    def __init__(self, port):
        self.controller = Controller()
        self.controller.start()
        self.serial = serial.Serial(port, BAUDRATE)
        self.h_speed, self.v_speed = 0, 0

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
        self.v_speed = event.value
        print(f"Movement speed {event.value}")

    def rx(self, event):
        # rotate
        self.h_speed = event.value
        print(f"Rotatating speed {event.value}")

    def h_arrows(self, event):
        # horizontal deplacement of the kart
        if event.value < 0:
            print("Moving kart to the left")
        elif event.value > 0:
            print("Moving kart to the right")

    def v_arrows(self, event):
        # vertical displacement of the kart
        if event.value < 0:
            print("Moving kart to the top")
        elif event.value > 0:
            print("Moving kart to the bottom")

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
            self.make_message(CAN, 0, 0)
            date = time.perf_counter_ns()
            # little movement either rotation or translation
            value = (self.h_speed, self.v_speed)[step]
            self.make_message((ROT, MOV)[step], 0, value + 0x10000 * (value < 0))
            step ^= True

            for event in self.controller.get_events():
                # gets the method corresponding to the event, if the event is not managed, it does nothing
                getattr(self, self.manage_event.get((event.type, event.button), 'nothing'))(event)

            # delays for 20 ms
            while time.perf_counter_ns() - date < 20_000_00:
                continue


if __name__ == '__main__':
    p = PS4Controll1A('/dev/ttyACM0')
    try:
        p.mainloop()
    except KeyboardInterrupt:
        p.controller.terminate()
        print()