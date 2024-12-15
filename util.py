"""
-- Agreement: --
No import high level objects in UTIL! (like classes)
"""

import math
import numpy as np
import numpy.typing as npt
import cv2 as cv
import ctypes
import mouse
import maus
import msvcrt
import random
import time
import win32gui

from itertools import groupby
from config import config


def pause(t=5):
    """
    Пауза длительностью t секунд.
    Можно остановить обратный отсчет, нажав любую клавишу.
    :param t:
    :return:
    """
    pressed = False
    print(f'Wait {t:.1f} sec, or type for pause')
    for i in range(round(t*10), 0, -1):
        if msvcrt.kbhit():
            # key = msvcrt.getch()
            pressed = True
            break
        print(f'\b\b\b{i/10:.1f}', end='')
        time.sleep(0.1)
    print('\b\b\b', end='')

    if pressed:
        print('Wait for key press')
        k = False
        while not k:
            k = msvcrt.kbhit()


def random_point_in_square(x, y, w, h):
    """
    x, y - координаты левого верхнего угла в пикселях
    w, h - ширина и высота прямоугольника
    :return: Случайную точку в этом прямоугольнике, с учетом безопасных полей.
    """
    safe_x, safe_y = int(w*0.2), int(h*0.2)

    x1, x2 = x + safe_x, x + w - safe_x
    y1, y2 = y + safe_y, y + h - safe_y
    xx = random.randint(x1, x2)
    yy = random.randint(y1, y2)
    return xx, yy


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


def search_pattern_in_image(pattern: npt.NDArray, image: npt.NDArray, precision: float):
    """
    Сканирует изображение image в поисках шаблона pattern (множественные вхождения).
    Возвращает два списка row_values и col_values. Начало координат - верх лево.

    Чем меньше значение precision, тем больше "похожих" клеток находит скрипт. При поиске клеток доски:
    При значении 0.6 он вообще зацикливается
    При значении 0.7 он находит closed cell в самых неожиданных местах
    Значение 0.9 выглядит ок, но на экране 2560х1440 находит несколько ячеек
    смещенных на 1 пиксель - это из-за того, что сами ячейки экрана имеют плавающий размер, при этом
    сами ячейки находятся нормально. Увеличение threshold при этом качество результата не увеличивает - смещены сами ячейки на экране.
    В результирующем списке ячейки расположены хаотично,
    поэтому нам нужно разобрать список координат отдельно по X и отдельно по Y, и создать 2D матрицу ячеек.

    :param pattern: образец, который надо найти в image
    :param image: изображение, например снимок экрана или взятое из файла
    :param precision - точность поиска, см. описание

    :return: cells_coord_x - список координаты по оси X для каждого столбца (в пикселях относительно верха лева экрана)
    :return: cells_coord_y - анал. по оси Y
    :rtype:
    """

    h, w = pattern.shape[:2]

    method = cv.TM_CCOEFF_NORMED
    # method = cv.TM_CCORR_NORMED

    res = cv.matchTemplate(image, pattern, method)

    # fake out max_val for first run through loop
    max_val = 1

    cells = []
    # debug - view found cells
    dc = win32gui.GetDC(0)

    while max_val > precision:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        if max_val > precision:
            res[max_loc[1] - h // 2:max_loc[1] + h // 2 + 1, max_loc[0] - w // 2:max_loc[0] + w // 2 + 1] = 0
            image = cv.rectangle(image, (max_loc[0], max_loc[1]), (max_loc[0] + w + 1, max_loc[1] + h + 1), (0, 255, 0))
            cellule = (max_loc[0], max_loc[1], max_val)
            cells.append(cellule)

            # debug - put digit on found cells
            # cv.putText(image, '1', (max_loc[0]+3, max_loc[1]+10), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)

            # debug - view found cells
            # x, y = max_loc[0], max_loc[1]
            # win32gui.Rectangle(dc, x + 3, y + 3, x + 8, y + 8)

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


def search_pattern_in_image_for_red_bombs(pattern: npt.NDArray, image: npt.NDArray):
    """
    Это немного тюнингованная версия search_pattern_in_image.
    Отличается настройками распознавания, заточенными под большие красные цифры (бомбы).

    Сканирует изображение image в поисках шаблона pattern (множественные вхождения).
    Возвращает два списка row_values и col_values. Начало координат - верх лево.

    Чем меньше значение precision, тем больше "похожих" клеток находит скрипт. При поиске клеток доски:
    При значении 0.6 он вообще зацикливается
    При значении 0.7 он находит closed cell в самых неожиданных местах
    Значение 0.9 выглядит ок, но на экране 2560х1440 находит несколько ячеек
    смещенных на 1 пиксель - это из-за того, что сами ячейки экрана имеют плавающий размер, при этом
    сами ячейки находятся нормально. Увеличение threshold при этом качество результата не увеличивает - смещены сами ячейки на экране.
    В результирующем списке ячейки расположены хаотично,
    поэтому нам нужно разобрать список координат отдельно по X и отдельно по Y, и создать 2D матрицу ячеек.

    :param pattern: образец, который надо найти в image
    :param image: изображение, например снимок экрана или взятое из файла
    :param precision - точность поиска, см. описание

    :return: cells_coord_x - список координаты по оси X для каждого столбца (в пикселях относительно верха лева экрана)
    :return: cells_coord_y - анал. по оси Y
    :rtype:
    """

    h, w = pattern.shape[:2]

    # method = cv.TM_CCOEFF
    # method = cv.TM_CCOEFF_NORMED  # ++
    # method = cv.TM_CCORR
    method = cv.TM_CCORR_NORMED  # ++
    # method = cv.TM_SQDIFF
    # method = cv.TM_SQDIFF_NORMED

    ### precision для TM_CCORR_NORMED, при котором удачно распознаются цифры (mine.online, 1920х1080, size 24)
    # bombs - min pecision - max precision
    # 099 - 0.937 - 0.944
    # 098 - 0.935 - 0.935
    # 098 - 0.931 - 0.944
    # 097 - 0.931 - 0.944
    # 096 - 0.929 - 0.944
    # 095 - 0.929 - 0.944
    # 094 - 0.929 - 0.944
    # 093 - 0.929 - 0.944
    # 092 - 0.929 - 0.944
    # 091 - 0.929 - 0.944
    # 090 - 0.929 - 0.944
    # 089 - 0.937 - 0.947
    # 088 - 0.935 - 0.947
    # 087 - 0.933 - 0.947

    precision = 0.940
    res = cv.matchTemplate(image, pattern, method)

    # fake out max_val for first run through loop
    max_val = 1

    cells = []
    # debug - view found cells
    dc = win32gui.GetDC(0)

    while max_val > precision:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        if max_val > precision:
            res[max_loc[1] - h // 2:max_loc[1] + h // 2 + 1, max_loc[0] - w // 2:max_loc[0] + w // 2 + 1] = 0
            image = cv.rectangle(image, (max_loc[0], max_loc[1]), (max_loc[0] + w + 1, max_loc[1] + h + 1), (0, 255, 0))
            cellule = (max_loc[0], max_loc[1], max_val)
            cells.append(cellule)

            # debug - put digit on found cells
            # cv.putText(image, '1', (max_loc[0]+3, max_loc[1]+10), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)

            # debug - view found cells
            x, y = max_loc[0], max_loc[1]
            win32gui.Rectangle(dc, x + 3, y + 3, x + 8, y + 8)

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



def point_in_rect(point, x1, y1, w, h):
    x2, y2 = x1 + w, y1 + h
    x, y = point
    if (x1 < x < x2) and (y1 < y < y2):
        return True
    return False


def cell_coordinates(cells):
    """
    Превращает список координат ВСЕХ ячеек поля в список отдельно X и Y координат
    :param cells: list of tuples (x, y, cv2_max_val)
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
    NOT USED
    Testing gaussian function for randomize time beetween clicks

    Look at action there:
    https://replit.com/@swasher/Gaussian-distribution-for-Minesweeper-mouse-duration
    """
    if config.mouse_duration > 0:
        mu = config.mouse_duration      # Значение в "центре" колокола
        sigma = config.mouse_gaussian   # Значения " по бокам" колокола, то есть отклонение от центра
        # deprecated
        # gauss = np.random.normal(mu, sigma, 1000)
        # gauss = gauss[gauss > config.minimum_delay]     # remove all negative and very small
        # return random.choice(gauss)
        gauss = abs(random.gauss(mu, sigma))
        return gauss
    else:
        return 0


if __name__ == '__main__':
    from timeit import Timer
    t = Timer(lambda: gauss_duration())
    print(t.timeit(number=1000))

