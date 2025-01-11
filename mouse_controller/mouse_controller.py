import time
import mouse
import math
import random
from config import config
import numpy as np
from .buttons import MouseButton as mb
from humancursor import SystemCursor

# FLAG = config.flag      # action `flag cell`
# OPEN = config.open      # action `open cell`
# NEARBY = config.nearby  # action `open all nearest by both click


def human_mouse_speed(distance):
    """
    Возвращает время в секундах, за которое человек провел бы мышью расстояние distance (в пикселях).
    Замеры смотри в track_mouse_when_man_playing.py
    :param distance: int
    :return: float
    """

    # пример значений для MINESWEEPER_ONLINE
    # дистанция - measured_distance = [30, 280, 660]
    # время - measured_duration = [0.41, 0.92, 1.03]

    measured_distance = config.measured_distance
    measured_duration = config.measured_duration

    # per100px = np.interp(distance, x, timeper100)
    # t = distance * per100px / 100

    t = np.interp(distance, measured_distance, measured_duration)/2

    return t


def click_mouse_lib(x, y, button: mb):
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

    if button in [mb.left, mb.right]:
        mouse.click(button=button.name)
    elif button == mb.both:
        mouse.press(button='left')
        mouse.press(button='right')
        mouse.release(button='left')
        mouse.release(button='right')

    # TODO add as `mouse_return` parameter
    if config.turn_by_turn:
        mouse.move(oldx, oldy)

    if config.extra_pause_between_clicks:
        time.sleep(config.extra_pause_between_clicks)


def click_systemcursor_lib(x, y, button: mb):
    cursor = SystemCursor()

    # можно использовать случайное время, или из моей либы human_mouse_speed
    oldx, oldy = mouse.get_position()
    dist = math.hypot(oldx - x, oldy - y)
    # duration = random.uniform(0.5, 2.0)
    duration = human_mouse_speed(dist)

    cursor.move_to((x, y), duration=duration, steady=True)

    # в SystemCursor применяются задержки, - время нажатия и время после отпускания, типа такого
    # pyautogui.mouseDown()
    # sleep(click_duration)
    # pyautogui.mouseUp()
    # sleep(random.uniform(0.170, 0.280))

    click_duration = random.uniform(0.01, 0.1)
    after_click_duration = random.uniform(0.17, 0.28)

    if button in [mb.left, mb.right]:
        # mouse.click(button=button.name)
        mouse.press(button=button.name)
        time.sleep(click_duration)
        mouse.release(button=button.name)
        time.sleep(after_click_duration)
    elif button == mb.both:
        mouse.press(button='left')
        mouse.press(button='right')
        mouse.release(button='left')
        mouse.release(button='right')

    if config.extra_pause_between_clicks:
        r = random.uniform(0.7, 1.3)
        time.sleep(config.extra_pause_between_clicks * r)


def click(x, y, button: mb):
    if config.use_neural_mouse:
        click_systemcursor_lib(x, y, button)
    else:
        click_mouse_lib(x, y, button)
