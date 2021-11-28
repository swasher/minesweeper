import mouse
import math
from config import config
import numpy as np

"""
class Maus(object):
    BOTH = 'both'

    def right_click(self):
        mouse

    def left_click(self):
        super()

    def both_click(self):
        mouse.press(button='left')
        mouse.press(button='right')
        mouse.release(button='left')
        mouse.release(button='right')

maus = Maus()


RIGHT = mouse.RIGHT
LEFT = mouse.LEFT
BOTH = 'both'
"""

# do set flag to cell
FLAG = config.flag
# do open cell
OPEN = config.open
# do open nearest cells by both click
NEARBY = config.nearby


def human_mouse_speed(distance):
    """
    Возвращает время в секундах, за которое человек проведет мышью расстояние distance (в пикселях).
    Замеры смотри в track_mouse_when_man_playing.py
    :param distance: int
    :return: float
    """
    x = [30, 280, 660]
    y = [1.47, 0.4, 0.17]
    per100px = np.interp(distance, x, y)
    t = distance * per100px / 100 / 3.5
    return t


# мы передаем некую сущность BUTTON из солвера, и она в итоге возвращается сюда - в click как button
def click(x, y, button):
    oldx, oldy = mouse.get_position()

    dist = math.hypot(oldx - x, oldy - y)
    # print(dist)
    # time.sleep(1)
    # mouse.move(x, y, absolute=True, duration=gauss_duration())
    duration = human_mouse_speed(dist)
    if duration < 0 or config.mouse_duration == 0:
        duration = 0
    mouse.move(x, y, absolute=True, duration=duration)

    if button in ['left', 'right']:
        mouse.click(button=button)
    elif button == 'both':
        mouse.press(button='left')
        mouse.press(button='right')
        mouse.release(button='left')
        mouse.release(button='right')

    # todo add as `mouse_return` parameter
    if config.turn_by_turn:
        mouse.move(oldx, oldy)
