"""
-- Agreement: --
No import high level objects in UTIL! (like classes)
"""

import os
import math
import numpy as np
import cv2 as cv
import ctypes
import mouse
import msvcrt
import random
import time
from itertools import groupby
from icecream import ic
from config import config


def pause(t=5):
    pressed = False
    print(f'Wait {t} sec, or type for pause')
    for i in range(t*10, 0, -1):
        if msvcrt.kbhit():
            # key = msvcrt.getch()
            pressed = True
            break
        # print(f'\b{i}')
        print(f'\b\b\b{i/10:.1f}', end='')
        time.sleep(0.1)
    print('\b\b\b', end='')

    if pressed:
        print('Wait for key press')
        k = False
        while not k:
            k = msvcrt.kbhit()


def click(x, y, button):
    oldx, oldy = mouse.get_position()

    from global_ import clicks
    clicks += 1

    dist = math.hypot(oldx - x, oldy - y)
    # print(dist)
    # time.sleep(1)
    mouse.move(x, y, absolute=True, duration=gauss_duration())

    if button in ['left', 'right']:
        mouse.click(button=button)
    elif button == 'both':
        mouse.press(button='left')
        mouse.press(button='right')
        mouse.release(button='left')
        mouse.release(button='right')

    if config.turn_by_turn:
        mouse.move(oldx, oldy)


def get_screen_size():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    size = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
    return size


def remove_dup(arr):
    """
    Remove dublicates from array of object.
    :return: array of Cellc
    """
    unique = list(set(arr))
    return unique


def compress_array(arr):
    """
    Удаляет из списка целые числа, которые находятся в близи difference друг к другу. Например:
    input [91, 91, 122, 123, 124, 154, 185, 217, 248, 279, 310, 311, 342, 374]
    difference 1
    output [91, 122, 124, 154, 185, 217, 248, 279, 310, 342, 374]

    Найдено тут. Как работает, хрен поймешь.
    https://stackoverflow.com/a/53177510/1334825


    :param arr: array of int
    :return: array of int
    """

    def runs(difference=1):
        start = None
        def inner(n):
            nonlocal start
            if start is None:
                start = n
            elif abs(start-n) > difference:
                start = n
            return start
        return inner

    newarr = [next(g) for k, g in groupby(sorted(arr), runs())]
    return newarr


# --- DEPRECATED
def find_templates(pattern, image, precision):

    """
    Эта функция не используется, но пусть будет тут, как альтернатива scan_region

    Ищет несколько вхождений темплейта в имадж.
    Координаты вхождений.

    Код отсюда
    https://stackoverflow.com/questions/61687427/python-opencv-append-matches-center-x-y-coordinates-in-tuples
    """

    h, w = pattern.shape[:2]
    # print('h', h, 'w', w)
    method = cv.TM_CCORR_NORMED

    res = cv.matchTemplate(image, pattern, method)
    res_h, res_w = res.shape[:2]

    # fake out max_val for first run through loop
    max_val = 1
    coords = []
    while max_val > precision:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if max_val > precision:
            coords.append((max_loc[0], max_loc[1], max_val))

            x1 = max(max_loc[0] - w//2, 0)
            y1 = max(max_loc[1] - h//2, 0)

            x2 = min(max_loc[0] + w//2, res_w)
            y2 = min(max_loc[1] + h//2, res_h)

            res[y1:y2, x1:x2] = 0

            # эта строка портит image для дальнейших сравнений в цикле
            # image = cv.rectangle(image, (max_loc[0], max_loc[1]), (max_loc[0]+w+1, max_loc[1]+h+1), (0,255,0) )

    """
    DEBUG
    возвращает координаты
    print(centers)
    cv.imshow("Test", image)
    cv.waitKey(0)
    """
    return coords


def search_pattern_in_image(pattern, image, precision):
    """
    Сканирует изображение image в поисках шаблона template (множественные вхождения).
    Возвращает два списка row_values и col_values. Начало координат - верх лево.

    Чем меньше значение precision, тем больше "похожих" клеток находит скрипт. При поиске клеток доски:
    При значении 0.6 он вообще зацикливается
    При значении 0.7 он находит closed cell в самых неожиданных местах
    Значение 0.9 выглядит ок, но на экране 2560х1440 находит несколько ячеек
    смещенных на 1 пиксель - это из-за того, что сами ячейки экрана имеют плавающий размер, при этом
    сами ячейки находятся нормально. Увеличение threshold при этом качество результата не увеличивает - смещены сами ячейки на экране.
    В результирующем списке ячейки расположены хаотично,
    поэтому нам нужно разобрать список координат отдельно по X и отдельно по Y, и создать 2D матрицу ячеек.

    :param image - изображение, например снимок экрана или взятое из файла
    :param template
    :param precision - точность поиска, см. описание

    :return: cells_coord_x - список координаты по оси X для каждого столбца (в пикселях относительно верха лева экрана)
    :return: cells_coord_y - анал. по оси Y
    :rtype:
    """

    h, w = pattern.shape[:2]

    method = cv.TM_CCOEFF_NORMED

    res = cv.matchTemplate(image, pattern, method)

    # fake out max_val for first run through loop
    max_val = 1

    cells = []
    while max_val > precision:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        if max_val > precision:
            res[max_loc[1] - h // 2:max_loc[1] + h // 2 + 1, max_loc[0] - w // 2:max_loc[0] + w // 2 + 1] = 0
            image = cv.rectangle(image, (max_loc[0], max_loc[1]), (max_loc[0] + w + 1, max_loc[1] + h + 1), (0, 255, 0))
            cellule = (max_loc[0], max_loc[1], max_val)
            cells.append(cellule)
            # `debug` cv.putText(image, str(x), (max_loc[0]+3, max_loc[1]+10), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)

    # # DEBUG; YOU CAN SEE WHAT GRABBING
    # # draw at each cell it's row and column number
    # for c in cells:
    #     x = c[1]
    #     y = c[0]
    #     cv.putText(image, str(x), (y + 11, x + 5), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
    #     cv.putText(image, str(y), (y + 19, x + 5), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
    # # cv.imwrite('output.png', image)
    # cv.imshow("Display window", image)
    # k = cv.waitKey(0)

    return cells


def cell_coordinates(cells):
    """
    Превращает список координат ВСЕХ ячеек поля в список отдельно X и Y координат
    :param cells: list of tuples (x, y, cv2 max_val)
    :return cells_coord_x: list of int, список координаты по оси X для каждого столбца (в пикселях относительно верха лева экрана)
    :return cells_coord_y: list of int, анал. по оси Y
    """

    cells_coord_y = []
    cells_coord_x = []
    for cell in cells:
        cells_coord_x.append(cell[0])
        cells_coord_y.append(cell[1])

    # Эти два списка - искомые координаты ячеек. Убираем из них дубликаты при помощи set()
    cells_coord_x = compress_array(cells_coord_x)  # кол-во соотв. кол-ву столбцов; координаты столбцов слева направо по X
    cells_coord_y = compress_array(cells_coord_y)  # кол-во соотв. кол-ву строк; координаты строк сверху вниз по Y

    return cells_coord_x, cells_coord_y


def gauss_duration():
    """
    Testing gaussian function for randomize time beetween clicks

    Look at action there:
    https://replit.com/@swasher/Gaussian-distribution-for-Minesweeper-mouse-duration
    """
    if config.mouse_duration > 0:
        mu = config.mouse_duration      # Значение в "центре" колокола
        sigma = config.mouse_gaussian   # Значения " по бокам" колокола, то есть отклонение от центра
        gauss = np.random.normal(mu, sigma, 1000)
        gauss = gauss[gauss > config.minimum_delay]     # remove all negative and very small
        return random.choice(gauss)
    else:
        return 0


if __name__ == '__main__':
    from timeit import Timer
    t = Timer(lambda: gauss_duration())
    print(t.timeit(number=1000))

