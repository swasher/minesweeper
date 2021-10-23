import random
import pyautogui
import winsound


def r(num, rand):
    return num + rand * random.random()


def click(x, y, button):
    DEBUG = True

    if DEBUG:
        oldx, oldy = pyautogui.position()

    timestamp = 0.1
    pyautogui.moveTo(x, y, timestamp)
    pyautogui.click(button=button)
    frequency = 2000  # Set Frequency To 2500 Hertz
    duration = 3  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)

    if DEBUG:
        pyautogui.moveTo(oldx, oldy)


def remove_dup(arr):
    """
    Remove dublicates from array of object.
    :return: array of Cellc
    """
    unique = list(set(arr))
    return unique


