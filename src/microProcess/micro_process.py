from base_micro import *
from constants import *
import time
import math


def empty():
    return
    yield


class MicroProcess(MicroManager):
    axle_track = AXLE_TRACK_1A
    log_level = DEBUG

    def __init__(self, lida_pipe, main_pipe, robot_x, robot_y, robot_heading, axle_track):
        self.robot_x, self.robot_y, self.robot_heading = robot_x, robot_y, robot_heading
        self.main_pipe, self.lidar_pipe = main_pipe, lida_pipe
        self.axle_track = axle_track
        MicroManager.__init__(self)

        self.last = [0, 0]
        self.routines = [empty(), empty()]
        self.run()

    def send(self, port, id_, comp, arg):
        if port not in self.serials:
            return print(f'{BOARDS[port]} is not connected')
        usb = self.serials[port]
        usb.send(usb.make_message(id_, comp, arg))

    def scan_feedbacks(self):
        if self.lidar_pipe.poll():
            pass
        if self.main_pipe.poll():
            type_, gen, args = self.main_pipe.recv()
            print(f"Received order from main: {type_}, {gen.__name__}, {args}")
            self.routines[type_] = gen(*args)
            self.next(type_)
        MicroManager.scan_feedbacks(self)

    def terminate(self, order_id, order_type):
        if order_id == self.last[order_type]:
            self.next(order_type)

    def next(self, type_):
        if self.log_level > NOT_NECESSARY:
            print(f'{type(self).__name__} : info : Next step of routine {self.routines[type_].__name__}({CATEGORIES[type_]})')
        # goes through the routine of the given type (MOVEMENT or ACTION)
        try:
            id_, comp, arg = next(self.routines[type_])
            self.last[type_] = id_
            if DESTINATION[id_] in self.serials:
                port = self.serials[DESTINATION[id_]]
                port.last_type = type_
                port.send(port.make_message(id_, comp, arg))
            else:
                self.log_method(f'{type(self).__name__} : info : {self.micro_classes[DESTINATION[id_]].__name__} is not connected')

        # routine is finished
        except StopIteration:
            self.pull(type_)

    def pull(self, type_):
        if self.log_level > NOT_NECESSARY:
            print(f'{type(self).__name__} : info : Asking next routine ({CATEGORIES[type_]})')
        # asks for a new routine of a given type
        self.main_pipe.send(type_)

    def run(self):
        try:
            self.pull(ACTION)
            self.pull(MOVEMENT)
            while True:
                self.scan_feedbacks()
        except KeyboardInterrupt:
            if PICO1 in self.serials:
                usb: BaseMicro = self.serials[PICO1]
                usb.send(usb.make_message(CAN, 0, 0))
            for usb in self.serials.values():
                usb.serial.close()


class MPGenericMicro(GenericMicro):
    master: MicroProcess
    last_type = 0

    def termination(self, message):
        order_id = message[0] & 0xf
        self.master.terminate(order_id, self.last_type)


class MPMovement(MovementMicro, MPGenericMicro):
    old_wheel = 0, 0

    def wheel_update(self, message):
        # tick positions for each wheel
        left, right = message[1] * 256 + message[2], message[3] * 256 + message[4]
        # Two's complement
        left -= 0x10000 * (left >= 0x8000)
        right -= 0x10000 * (right >= 0x8000)

        d_left, d_right = left - self.old_wheel[0], right - self.old_wheel[1]
        self.old_wheel = left, right

        left_arc, right_arc = (
            2 * math.pi * d_left * WHEEL_RADIUS / TICKS_PER_REVOLUTION,
            2 * math.pi * d_right * WHEEL_RADIUS / TICKS_PER_REVOLUTION
        )

        # straight movement
        if d_left == d_right:
            self.master.robot_x.value += left_arc * math.cos(self.master.robot_heading)
            self.master.robot_y.value += left_arc * math.sin(self.master.robot_heading)
            return

        # circular movement
        radius = .5 * self.master.axle_track * (d_left + d_right) / (d_right - d_left)
        angle = (right_arc - left_arc) / self.master.axle_track
        a0, a1 = self.master.robot_heading - math.pi * .5, self.master.robot_heading - math.pi * .5 + angle
        self.master.robot_x.value += radius * (math.cos(a1) - math.cos(a0))
        self.master.robot_y.value += radius * (math.sin(a1) - math.sin(a0))
        self.master.robot_heading.value += angle


class MPAction(ActionMicro, MPGenericMicro):
    pass


class MPArduinoMicro(ArduinoMicro, MPGenericMicro):
    pass


MicroProcess.micro_classes = MPMovement, MPAction, MPArduinoMicro

if __name__ == '__main__':
    MP = MicroProcess(None, None, None, None, None, 1.)
    print(MP.serials)
