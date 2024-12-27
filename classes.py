import random
import win32api
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


class Color():
    red: win32api.RGB(255, 0, 0)
    green: win32api.RGB(0, 255, 0)
    blue: win32api.RGB(0, 0, 255)
    yellow: win32api.RGB(255, 255, 0)
    cyan: win32api.RGB(0, 255, 255)
    magenta: win32api.RGB(255, 0, 255)

    def rand(self):
        colors = [value for name, value in vars(self.__class__).items() if not name.startswith('__') and not callable(value)]
        return random.choice(colors)