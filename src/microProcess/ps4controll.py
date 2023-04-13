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
        print(self.serials)


        self.h_speed, self.v_speed = 0, 0
        self.left_target, self.right_target = 0, 0
        self.positions = [2, 3]
        self.moving_arm, self.pump = False, False
        self.last = [0, 0]

    @staticmethod
    def set_arm_x(dx):
        dx = dx + 0x10000 * (dx < 0)
        return ARM, 0, (dx << 16) | dx

    @staticmethod
    def set_arm_y(dy):
        n_dy = -dy
        dy = dy + 0x10000 * (dy < 0)
        n_dy = -n_dy + 0x10000 * (n_dy < 0)
        return ARM, 0, (dy << 16) | n_dy

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
            self.send(PICO2, PUM, 1, 1)
            print('Catching the cake')

    def circle(self, event):
        # drop cake
        if event.value:
            self.send(PICO2, PUM, 1, 0)
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
        # print(f"Rotating speed {event.value}")

    def h_arrows(self, event):
        # horizontal displacement of the kart
        if not self.last[0] and event.value and not self.moving_arm:
            if event.value > 0 and self.positions[0] + 1 < len(HORIZONTAL_POSITIONS):
                new_p = self.positions[0] + 1
                self.send(PICO2, *self.set_arm_x(HORIZONTAL_POSITIONS[new_p] - HORIZONTAL_POSITIONS[self.positions[0]]))
                self.positions[0] = new_p
            elif event.value < 0 and self.positions[0]:
                new_p = self.positions[0] - 1
                self.send(PICO2, *self.set_arm_x(HORIZONTAL_POSITIONS[new_p] - HORIZONTAL_POSITIONS[self.positions[0]]))
                self.positions[0] = new_p
        self.last[0] = event.value

    def v_arrows(self, event):
        # vertical displacement of the kart
        if not self.last[1] and event.value and not self.moving_arm:
            if event.value > 0 and self.positions[1] + 1 < len(VERTICAL_POSITIONS):
                new_p = self.positions[1] + 1
                self.send(PICO2, *self.set_arm_y(HORIZONTAL_POSITIONS[new_p] - HORIZONTAL_POSITIONS[self.positions[1]]))
                self.positions[1] = new_p
            elif event.value < 0 and self.positions[1]:
                new_p = self.positions[1] - 1
                self.send(PICO2, *self.set_arm_y(HORIZONTAL_POSITIONS[new_p] - HORIZONTAL_POSITIONS[self.positions[1]]))
                self.positions[1] = new_p
        self.last[0] = event.value

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

            # delays for 20 ms
            while time.perf_counter() - date < .02:
                for event in self.controller.get_events():
                    # gets the method corresponding to the event, if the event is not managed, it does nothing
                    getattr(self, self.manage_event.get((event.type, event.button), 'nothing'))(event)
                self.scan_feedbacks()


class PS4Generic(GenericMicro):
    master: PS4Control1A

    def termination(self, message):
        if message[0] & 0xf == ARM:
            self.master.moving_arm = False


class PS4Movement(MovementMicro, PS4Generic):
    pass


class PS4Action(ActionMicro, PS4Generic):
    pass


class PS4Arduino(ArduinoMicro, PS4Generic):
    pass


PS4Control1A.micro_classes = PS4Movement, PS4Action, PS4Arduino


if __name__ == '__main__':
    p = PS4Control1A()
    try:
        p.mainloop()
    except KeyboardInterrupt:
        p.controller.terminate()
        print()
