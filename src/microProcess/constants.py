import math

ORDER_LENGTH = 5
FEEDBACK_LENGTH = 5
BAUDRATE = 115200

# log modes
NOTHING, NECESSARY, EVERYTHING = range(3)
LOG_MODES = 'nothing', 'necessary', 'everything'

# log priorities
NEC, N_NEC = range(2)  # Necessary, Not Necessary

# Feedbacks
ACK, TER, VAR, TRA, ERR, WHE = range(6)
FEEDBACKS = 'ACKNOWLEDGEMENT', 'TERMINAISON', 'VAR_GET', 'TRACKED', 'ERROR', 'WHEEL_UPDATE'

# orders
# c.f. https://docs.google.com/spreadsheets/d/1NDprMKYs9L7S2TkqgACDOh6OKDJRHhz_LrTCKmEuD-k/edit#gid=0
LID, MOV, ROT, CAN, MOT_VALUE, MOT_TIME, PUM, MOTS, MOTS_A, VAR_SET, VAR_GET, TRACK, _, _, _, _ = range(16)
ORDERS = (
    'LIDAR', 'MOVE', 'ROT', 'CANCEL', 'MOT_VALUE', 'MOT_TIME', 'PUMPS', 'MOTS', 'MOTS_A', 'VAR_SET', 'VAR_GET', 'TRACK',
    '', '', '', ''
)


# order types
MOVEMENT, ACTION, OTHER = range(3)
CATEGORIES = 'MOVEMENT', 'ACTION', 'OTHER'

# correspondance of an order type to each order
TYPES = (
    OTHER, MOVEMENT, MOVEMENT, MOVEMENT, ACTION, ACTION, ACTION, ACTION, ACTION, OTHER, OTHER, OTHER, None, None, None,
    None
)

# --------------------------------------------------------- Physics ----------------------------------------------------

# arbitrary values to compute robot movement
AXLE_TRACK_1A, AXLE_TRACK_2A = .2, .2
TICKS_PER_REVOLUTION = 1024
WHEEL_RADIUS = .1


# --------------------------------------------------------- Shell.py ---------------------------------------------------

# PID variables
VAR_NAMES = (
    'motorKi', 'motorKp', 'motorKd', 'wheelKi', 'wheelKp', 'wheelKd'
)
VAR_DICT = {n: i for i, n in enumerate(VAR_NAMES)}


# Limits of arguments
MIN_TICKS, MAX_TICKS = -32768, 32768  # valid range of tick arguments
MIN_T_MS, MAX_T_MS = 0, 65536  # valid range of time arguments in ms

MAX_DISTANCE = 2 * math.pi * WHEEL_RADIUS * MAX_TICKS / TICKS_PER_REVOLUTION  # maximum distance covered by goto
