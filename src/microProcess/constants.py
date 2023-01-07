#  log modes
NOTHING, NECESSARY, EVERYTHING = range(3)
LOG_MODES = 'nothing', 'necessary', 'everything'

#  log priorities
NEC, N_NEC = range(2)

#  order types
MOVEMENT, ACTION, OTHER = range(3)
CATEGORIES = 'MOVEMENT', 'ACTION', 'OTHER'

#  orders
LID, MOV, ROT, CAN, MOT_VALUE, MOT_TIME, PUM, MOTS, MOTS_A, VAR_SET, VAR_GET, TRACK, _, _, _, _ = range(16)
ORDERS = (
    'LIDAR', 'MOVE', 'ROT', 'CANCEL', 'MOT_VALUE', 'MOT_TIME', 'PUMPS', 'MOTS', 'MOTS_A', 'VAR_SET', 'VAR_GET', 'TRACK',
    '', '', '', ''
)
TYPES = (
    OTHER, MOVEMENT, MOVEMENT, MOVEMENT, ACTION, ACTION, ACTION, ACTION, ACTION, OTHER, OTHER, OTHER, None, None, None, None
)


#  PID variables
VAR_NAMES = (
    'motorKi', 'motorKp', 'motorKd', 'wheelKi', 'wheelKp', 'wheelKd'
)
VAR_DICT = {n: i for i, n in enumerate(VAR_NAMES)}

#  Feedbacks
ACK, TER, VAR, TRA = range(4)
FEEDBACKS = 'ACKNOWLEDGEMENT', 'TERMINAISON', 'GET_VAR', 'TRACKED'


# Limits of arguments
MIN_TICKS, MAX_TICKS = -32768, 32768
MIN_T_MS, MAX_T_MS = 0, 65536
