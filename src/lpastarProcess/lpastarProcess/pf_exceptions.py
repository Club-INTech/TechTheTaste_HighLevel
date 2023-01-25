class EmptyQueueException(RuntimeError):
    def __init__(self, arg):
        self.args = arg


class ImpossibleTransitionException(RuntimeError):
    def __init__(self, arg):
        self.args = arg


class MapInitializationException(RuntimeError):
    def __init__(self, arg):
        self.args = arg


class PathDoesNotExistException(RuntimeError):
    def __init__(self, arg):
        self.args = arg


class TimeoutException(RuntimeError):
    def __init__(self, arg):
        self.args = arg
