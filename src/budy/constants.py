from enum import StrEnum, auto

APP_NAME = "budy"
MIN_YEAR = 1900
MAX_YEAR = 2100


class Bank(StrEnum):
    LHV = auto()
    SEB = auto()
    SWEDBANK = auto()
