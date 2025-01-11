import random
import win32api
from enum import IntEnum
from config import config
from mouse_controller import MouseButton


class State(IntEnum):
    playing = 0
    win = 1
    fail = 2


class Action(IntEnum):
    open_cell = 0
    open_digit = 1
    set_flag = 2

    def __str__(self):
        # return f'{self.__class__.__name__}.{self.name}'
        match self:
            case self.open_cell:
                return 'open'
            case self.open_digit:
                return 'open'
            case self.set_flag:
                return 'flag'

    @property
    def button(self):
        if self == Action.open_cell:
            return MouseButton(config.open_button)
        elif self == Action.open_digit:
            return MouseButton(config.nearby_button)
        elif self == Action.set_flag:
            return MouseButton(config.flag_button)


class Color:
    red = win32api.RGB(255, 0, 0)
    green = win32api.RGB(0, 255, 0)
    blue = win32api.RGB(0, 0, 255)
    yellow = win32api.RGB(255, 255, 0)
    cyan = win32api.RGB(0, 255, 255)
    magenta = win32api.RGB(255, 0, 255)

    def rand(self):
        colors = [value for name, value in vars(self.__class__).items() if not name.startswith('__') and not callable(value)]
        return random.choice(colors)