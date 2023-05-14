import math

ORDER_LENGTH = 5
FEEDBACK_LENGTH = 5
BAUDRATE = 115200

SYNC_BYTES = b'\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9'

# log modes
NOTHING, MINIMAL, DEBUG = range(3)
LOG_MODES = 'nothing', 'minimal', 'debug'

# log priorities
NECESSARY, NOT_NECESSARY = range(2)

# Feedbacks
ACK, TER, VAR, TRA, ERR,  WHE, DEB, ID_F = range(8)
FEEDBACKS = 'ACKNOWLEDGEMENT', 'TERMINATION', 'VAR_GET', 'TRACKED', 'ERROR', 'WHEEL_UPDATE', 'DEBUG', 'IDENTIFY'

# orders
# c.f. https://docs.google.com/spreadsheets/d/1NDprMKYs9L7S2TkqgACDOh6OKDJRHhz_LrTCKmEuD-k/edit#gid=0
LID, MOV, ROT, CAN, ARM, _, PUM, _, _, VAR_SET, VAR_GET, TRACK, _, _, LATCH, ID = range(16)
ORDERS = (
    'LIDAR', 'MOVE', 'ROT', 'CANCEL', 'ARM', '', 'PUMPS', '', '', 'VAR_SET', 'VAR_GET', 'TRACK',
    '', '', 'LATCH', 'ID'
)


# order types
MOVEMENT, ACTION, OTHER = range(3)
CATEGORIES = 'MOVEMENT', 'ACTION', 'OTHER'

# correspondence of an order type to each order
TYPES = (
    OTHER, MOVEMENT, MOVEMENT, MOVEMENT, ACTION, None, ACTION, None, None, MOVEMENT, MOVEMENT, MOVEMENT, None, None, OTHER,
    OTHER
)


# controllers
PICO1, PICO2, ARDUINO, WHO_CARES = range(4)
BOARDS = 'MovementPico', 'ActionPico', 'Arduino'
# correspondence of a controller to each order
DESTINATION = (
    PICO1, PICO1, PICO1, PICO1, PICO2, WHO_CARES, PICO2, WHO_CARES, WHO_CARES, PICO1, PICO1, PICO1, WHO_CARES,
    WHO_CARES, ARDUINO, WHO_CARES
)


# --------------------------------------------------------- Physics ----------------------------------------------------

AXLE_TRACK_1A, AXLE_TRACK_2A = .213, .274  # in m, +- 1mm, measurements 18/02/2023 ~17h
TICKS_PER_REVOLUTION = 1024
WHEEL_RADIUS = .0340  # in m, +- 0.1mm, measurements 18/02/2023 ~17h coupling both wheels of both robots


# --------------------------------------------------------- Shell.py ---------------------------------------------------

# pdi right left trans rot
# PID variables
VAR_NAMES = (
    'Kp_rot', 'Kd_rot', 'Ki_rot', 'Kp_trans', 'Kd_trans', 'Ki_trans', 'vitesse'
)
VAR_DESTINATION = (
    PICO1, PICO1, PICO1, PICO1, PICO1, PICO1, PICO2
)
VAR_DICT = {n: i for i, n in enumerate(VAR_NAMES)}


# Limits of arguments
MIN_TICKS, MAX_TICKS = -32768, 32768  # valid range of tick arguments
MIN_T_MS, MAX_T_MS = 0, 65536  # valid range of time arguments in ms

MAX_DISTANCE = 2 * math.pi * WHEEL_RADIUS * MAX_TICKS / TICKS_PER_REVOLUTION  # maximum distance covered by goto

# facing the robot
LEFT, MID, RIGHT = range(3)
HORIZONTAL_POSITIONS = LEFT_SLOT, MID_SLOT, RIGHT_SLOT = 0, 705, 1410
TOP = 0
LOWEST_CAKE, CAKE_HEIGHT = -580, 80
