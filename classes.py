from enum import IntEnum
from config import config


class Action(IntEnum):
    open_cell = 1
    open_digit = 2
    set_flag = 3

    def __str__(self):
        return f'{self.__class__.__name__}.{self.name}'

    @property
    def button(self):
        if self == Action.open_cell:
            return MouseButtons(config.open_button)
        elif self == Action.open_digit:
            return MouseButtons(config.nearby_button)
        elif self == Action.set_flag:
            return MouseButtons(config.flag_button)


class MouseButtons(IntEnum):
    left = 1
    right = 2
    both = 3

    def __str__(self):
        return f'{self.__class__.__name__}.{self.name}'

    @classmethod
    def _missing_(cls, value):
        if type(value) is str:
            value = value.lower()
            if value in dir(cls):
                return cls[value]
