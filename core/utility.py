import random

from dataclasses import dataclass
from enum import IntEnum
from config import config
from mouse_controller import MouseButton




class MineMode(IntEnum):
    PREDEFINED = 0
    UNDEFINED = 1


class GameState(IntEnum):
    playing = 0
    win = 1
    fail = 2
    waiting = 3  # состояние в Tk до начала игры (до первого клика)


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


