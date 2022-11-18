LOG_NOTHING, LOG_NECESSARY, LOG_EVERYTHING = range(3)
NECESSARY, NOT_NECESSARY = range(1, 3)


# orders
LIDAR, FORWARDS, ROTATE, CANCEL, MOTOR_TICKS, MOTOR_TIME, SET_PUMPS, MOTORS, MOTORS_ARG, _, _, _, _, _, _, _ = \
    range(16)
ORDERS = (
    'LIDAR', 'FORWARDS', 'ROTATE', 'CANCEL', 'MOTOR_TICKS', 'MOTOR_TIME', 'SET_PUMPS', 'MOTORS', 'MOTORS_ARG', '', '',
    '', '', '', '', ''
)

FEED_BACKS = (
    'ACKNOWLEDGEMENT', 'TERMINAISON'
)


# order categories
MOVEMENT, ACTION, OTHER = range(3)

CATEGORIES = 'MOVEMENT', 'ACTION', 'OTHER'

TYPES = (  # Assigns every order to its type
    OTHER, MOVEMENT, MOVEMENT, OTHER, ACTION, ACTION, ACTION, ACTION, ACTION, None, None, None, None, None, None, None
)
