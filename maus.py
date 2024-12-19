import time
import mouse
import math
from config import config
import numpy as np

FLAG = config.flag      # action `flag cell`
OPEN = config.open      # action `open cell`
NEARBY = config.nearby  # action `open all nearest by both click


def human_mouse_speed(distance):
    """
    Возвращает время в секундах, за которое человек провел бы мышью расстояние distance (в пикселях).
    Замеры смотри в track_mouse_when_man_playing.py
    :param distance: int
    :return: float
    """


    # # MINESWEEPER_ONLINE
    # # distance
    # measured_distance = [30, 280, 660]
    # # time
    # measured_duration = [0.41, 0.92, 1.03]
    #
    #
    # # VIENNA
    # # distance
    # measured_distance = [18.88, 150.6, 315.35]
    # # time
    # measured_duration = [0.45, 1.05, 1.05]

    measured_distance = config.measured_distance
    measured_duration = config.measured_duration

    # per100px = np.interp(distance, x, timeper100)
    # t = distance * per100px / 100

    t = np.interp(distance, measured_distance, measured_duration)/2

    return t


def click(x, y, action):
    oldx, oldy = mouse.get_position()

    dist = math.hypot(oldx - x, oldy - y)
    # print(dist)
    # time.sleep(1)
    # mouse.move(x, y, absolute=True, duration=gauss_duration())
    duration = human_mouse_speed(dist)
    if duration < 0:
        duration = 0
    if config.minimum_delay_between_clicks > duration:
        duration = config.minimum_delay_between_clicks
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

    if config.extra_pause_between_clicks:
        time.sleep(config.extra_pause_between_clicks)
        print('SLEEP!')
