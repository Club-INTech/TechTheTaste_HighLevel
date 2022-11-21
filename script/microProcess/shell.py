from micro import MicroProcess
from constants import *
import sys
import cmd


class Shell(cmd.Cmd):
    def __init__(self, m_proc: MicroProcess):
        self.m_proc = m_proc
        cmd.Cmd.__init__(self)
        self.prompt = f'{self.m_proc} |> '

    def do_move(self, line):
        """
Command: move
move [sign: 1 | -1] [0 <= ticks < 65536]
Robot will move <ticks> ticks forward if sign is 1, backwards if sign is -1
"""
        print(line.split())

    def do_rotate(self, line):
        """
Command: rotate
rotate [sign: 1 | -1] [0 <= ticks < 65536]
Robot will rotate around its center for <ticks> ticks (clockwise: sign is 1, couterclockwise: sign is -1)
"""
        print(line.split())

    def do_motor_value(self, line):
        """
Command: motor_value
motor_value [0 <= motor_id < 16] [0 <= t < 65536]
Rotates stepper motor <motor_id> of m + t * (M - n) / 65536
m, M being minimal and maximal positions of the motor
"""
        print(line.split())

    def do_motor_time(self, line):
        """
Command: motor_time
motor_time [0 <= motor_id < 16] [0 <= ms < 65536]
Rotates motor <motor_id> during <ms> ms at its velocity
"""
        print(line.split())

    def do_set_pumps(self, line):
        """
Command: set_pumps
set_pumps *[0 <= pump_ids < 16]
sets every pump in pump_ids on other will be off
"""
        print(line.split())

    def do_motors(self, line):
        """
Command: motors
motors *([0 <= motor_id < 16] [0 <= t < 65536])
same as motor_value but for multiple motors
"""
        print(line.split())

    def do_set_var(self, line):
        """
Command set_var
set_var [var_name] [value]
sets the variable <var_name> to <value> in the raspberry Pico chip
"""
        print(line.split())

    def do_get_var(self, line):
        """
Command get_var
get_var [var_name]
shows the value of variable <var_name> in the raspberry Pico chip
"""
        print(line.split())

    def do_EOF(self, line):
        return True


if __name__ == '__main__':
    log_arg = LOG_NOTHING if len(sys.argv) < 3 else \
        {'LOG_NOTHING': LOG_NOTHING, 'LOG_NECESSARY': LOG_NECESSARY, 'LOG_EVERYTHING': LOG_EVERYTHING}[sys.argv[2]]
    Shell(MicroProcess(sys.argv[1], 115200, None, None, log_level=log_arg)).cmdloop()
