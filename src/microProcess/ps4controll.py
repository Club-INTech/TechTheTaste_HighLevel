from controller import get, end
from base_micro import BaseMicro
from constants import *
import serial
import time


class PS4Controll1A(BaseMicro):
    def __init__(self, port, baudrate):
        self.serial = serial.Serial(port, baudrate)
        self.h_speed, self.v_speed = 0, 0

    def nothing(self, event):
        # void function
        pass

    n = nothing

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

    manage = (
        type('', (), {'__getitem__': lambda self, it: PS4Controll1A.nothing})(),
        (cross, circle, triangle) + (n,) * 10,
        (n, ly, n, rx, n, n, h_arrows, v_arrows),
        (n,) * 2
    )

    def mainloop(self):
        step = False
        while True:
            self.make_message(CAN, 0, 0)
            date = time.perf_counter_ns()
            value = (self.h_speed, self.v_speed)[step]
            self.make_message((ROT, MOV)[step], 0, value + 0x100 * (value < 0))
            step ^= True

            for event in get():
                self.manage[event.type][event.button](self, event)

            while time.perf_counter_ns() - date < 20_000:
                continue

    def __repr__(self):
        return 'PS4 Controller'


if __name__ == '__main__':
    try:
        PS4Controll1A('/dev/ttyACM0', 115200).mainloop()
    except KeyboardInterrupt:
        end()
        print()
