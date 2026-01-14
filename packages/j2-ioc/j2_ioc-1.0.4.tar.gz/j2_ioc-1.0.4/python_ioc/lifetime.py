from enum import Enum, auto


class Lifetime(Enum):
    TRANSIENT = auto()
    SCOPED = auto()
    SINGLETON = auto()
