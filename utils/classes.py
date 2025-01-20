import random
import win32api
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


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
