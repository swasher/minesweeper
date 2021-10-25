import cv2 as cv
import numpy as np
import random
import pyautogui
import winsound
import mss
from itertools import groupby
from icecream import ic


def r(num, rand):
    return num + rand * random.random()


def click(x, y, button):
    DEBUG = False

    if DEBUG:
        oldx, oldy = pyautogui.position()

    timestamp = 0.2
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



def find_templates(pattern, image, precision):

    """
    Эта функция не используется, но пусть будет тут, как альтернатива scan_region

    Ищет несколько вхождений темплейта в имадж.
    Координаты вхождений.

    Код отсюда
    https://stackoverflow.com/questions/61687427/python-opencv-append-matches-center-x-y-coordinates-in-tuples
    """

    h, w = pattern.shape[:2]

    print('h', h, 'w', w)

    method = cv.TM_CCORR_NORMED

    res = cv.matchTemplate(image, pattern, method)
    res_h, res_w = res.shape[:2]

    # fake out max_val for first run through loop
    max_val = 1
    centers = []
    while max_val > precision:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if max_val > precision:
            centers.append( (max_loc[0] + w//2, max_loc[1] + h//2) )

            x1 = max(max_loc[0] - w//2, 0)
            y1 = max(max_loc[1] - h//2, 0)

            x2 = min(max_loc[0] + w//2, res_w)
            y2 = min(max_loc[1] + h//2, res_h)

            res[y1:y2, x1:x2] = 0

            image = cv.rectangle(image, (max_loc[0], max_loc[1]), (max_loc[0]+w+1, max_loc[1]+h+1), (0,255,0) )

    """
    DEBUG
    возвращает координаты
    print(centers)
    cv.imshow("Test", image)
    cv.waitKey(0)
    """
    return centers


def scan_region(region, template):
    """
    Сканирует экран или область region в поисках шаблона samplefile
    Возвращает два списка row_values и col_values. Начало координат - верх лево.

    :param region - tuple of [left, top, width, height]
    :param samplefile

    :return: cells_coord_x - список координаты по оси X для каждого столбца (в пикселях относительно верха лева экрана)
    :return: cells_coord_y - анал. по оси Y
    :rtype:
    """
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        raw = np.array(screenshot)
        image = cv.cvtColor(raw, cv.COLOR_BGRA2BGR)

        h, w = template.shape[:2]

        method = cv.TM_CCOEFF_NORMED

        threshold = 0.90  # Чем меньше это значение, тем больше "похожих" клеток находит скрипт.
                         # При значении 0.6 он вообще зацикливается
                         # При значении 0.7 он находит closed cell в самых неожиданных местах
                         # Значение 0.9 выглядит ок, но на экране 2560х1440 находит несколько ячеек
                         #    смещенных на 1 пиксель - это из-за того, что сами ячейки экрана имеют плавающий размер, при этом
                         # сами ячейки находятся нормально. Увеличение threshold при этом качество результата не увеличивает - смещены сами ячейки на экране.
                         # В результирующем списке ячейки расположены хаотично,
                         # поэтому нам нужно разобрать список координат отдельно по X и отдельно по Y, и создать 2D матрицу ячеек.

        res = cv.matchTemplate(image, template, method)

        # fake out max_val for first run through loop
        max_val = 1

        cells = []
        while max_val > threshold:
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

            if max_val > threshold:
                res[max_loc[1] - h // 2:max_loc[1] + h // 2 + 1, max_loc[0] - w // 2:max_loc[0] + w // 2 + 1] = 0
                image = cv.rectangle(image, (max_loc[0], max_loc[1]), (max_loc[0] + w + 1, max_loc[1] + h + 1), (0, 255, 0))
                cellule = (max_loc[0], max_loc[1])
                cells.append(cellule)
                # cv.putText(image, str(x), (max_loc[0]+3, max_loc[1]+10), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)

        cells_coord_y = []
        cells_coord_x = []
        for cell in cells:
            cells_coord_x.append(cell[0])
            cells_coord_y.append(cell[1])

        # Эти два списка - искомые координаты ячеек. Убираем из них дубликаты при помощи set()
        cells_coord_x = compress_array(cells_coord_x)  # кол-во соотв. кол-ву столбцов; координаты столбцов слева направо по X
        cells_coord_y = compress_array(cells_coord_y)  # кол-во соотв. кол-ву строк; координаты строк сверху вниз по Y

        num_rows = len(cells_coord_y)
        num_cols = len(cells_coord_x)
        total_cells = len(cells_coord_y) * len(cells_coord_x)

        ic(num_rows)
        ic(num_cols)
        ic(total_cells)

        """
        # for test purpose; YOU CAN SEE WHAT GRABBING
        # draw at each cell it's row and column number
        for col, x in enumerate(cells_coord_x):
            for row, y in enumerate(cells_coord_y):
                cv.putText(image, str(row), (x + 5, y + 11), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
                cv.putText(image, str(col), (x + 5, y + 19), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
        # cv.imwrite('output.png', image)
        cv.imshow("Display window", image)
        k = cv.waitKey(0)
        """

    return cells_coord_y, cells_coord_x