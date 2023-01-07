from controller import get, end
from base_micro import BaseMicro
import serial


class PS4Controll1A(BaseMicro):
    def __init__(self, port, baudrate):
        self.serial = serial.Serial(port, baudrate)

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
        print(f"Movement speed {event.value}")

    def rx(self, event):
        # rotate
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
        while True:
            for event in get():
                self.manage[event.type][event.button](self, event)


if __name__ == '__main__':
    try:
        PS4Controll1A('/dev/ttyACM0', 115200).mainloop()
    except KeyboardInterrupt:
        end()
        print()
