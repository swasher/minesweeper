import random
import mss
import numpy as np
import cv2 as cv
import pyautogui
import winsound
import classes


def r(num, rand):
    return num + rand * random.random()


def click(x, y, button):
    # x += classes.Matrix.region_x1
    # y += classes.Matrix.region_y1
    timestamp = 1
    pyautogui.moveTo(x, y, timestamp)
    pyautogui.click(button=button)
    frequency = 2000  # Set Frequency To 2500 Hertz
    duration = 3  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)


def remove_dup(arr):
    """
    Remove dublicates from array of arrays.
    Found there https://stackoverflow.com/a/69283440/1334825
    :return:
    """
    k = list(map(tuple, arr))
    unique = list(dict.fromkeys(k))
    return unique