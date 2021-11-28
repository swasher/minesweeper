import mouse
import math
from config import config
import numpy as np

FLAG = config.flag      # action `flag cell`
OPEN = config.open      # action `open cell`
NEARBY = config.nearby  # action `open all nearest by both click

import time
def human_mouse_speed(distance):
    """
    Возвращает время в секундах, за которое человек проведет мышью расстояние distance (в пикселях).
    Замеры смотри в track_mouse_when_man_playing.py
    :param distance: int
    :return: float
    """

    """ # mine online
    # distance
    x = [30, 280, 660]
    # time per 100 px
    y = [1.47, 0.4, 0.17]
    # time
    tim = [0.41, 0.92, 1.03]
    """

    # VIENNA
    # distance
    x = [18.88, 150.6, 315.35]
    # time per 100 px
    timeper100 = [2.93, 0.74, 0.36]
    # time
    y = [0.45, 1.05, 1.05]

    # per100px = np.interp(distance, x, timeper100)
    # t = distance * per100px / 100

    t = np.interp(distance, x, y)/10

    return t


def click(x, y, action):
    oldx, oldy = mouse.get_position()

    dist = math.hypot(oldx - x, oldy - y)
    # print(dist)
    # time.sleep(1)
    # mouse.move(x, y, absolute=True, duration=gauss_duration())
    duration = human_mouse_speed(dist)
    if duration < 0 or config.mouse_duration == 0:
        duration = 0
    mouse.move(x, y, absolute=True, duration=duration)

    if action in ['left', 'right']:
        mouse.click(button=action)
    elif action == 'both':
        mouse.press(button='left')
        mouse.press(button='right')
        mouse.release(button='left')
        mouse.release(button='right')

    # TODO add as `mouse_return` parameter
    if config.turn_by_turn:
        mouse.move(oldx, oldy)
