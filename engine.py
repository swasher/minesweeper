import random

import cv2 as cv
import icecream
import mss
import numpy as np
import pyautogui
import time
from icecream import ic
icecream.install()

from classes import Cell, Matrix
from solve import solve

def scan_region(region):
    """
    :param region
    Возвращает два списка row_values и col_values. Начало координат - верх лево.
    row_values - список координаты по оси X для каждого столбца
    row_values - список координаты по оси Y для каждой строки
    :return:
    """
    with mss.mss() as sct:
        # for prod
        screenshot = sct.grab(region)
        raw = np.array(screenshot)
        image = cv.cvtColor(raw, cv.COLOR_RGB2BGR)

        # for dev
        # image = cv.imread('pic/test_big.png', cv.IMREAD_COLOR)

        template = cv.imread('pic/closed.png', cv.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError('Image file not found: {}'.format(image))

        h, w = template.shape[:2]

        method = cv.TM_CCOEFF_NORMED

        threshold = 0.90

        start_time = time.time()

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

        row_values = []
        col_values = []
        for i in cells:
            col_values.append(i[0])
            row_values.append(i[1])

        # Эти два списка - искомые координаты ячеек
        row_values = sorted(list(set(row_values)))  # кол-во соотв. кол-ву строк; координаты строк сверху вниз - Y
        col_values = sorted(list(set(col_values)))  # кол-во соотв. кол-ву столбцов; координаты столбцов слева направо - X

        num_rows = len(row_values)
        num_cols = len(col_values)
        total_cells = len(row_values) * len(col_values)

        ic(num_rows)
        ic(num_cols)
        ic(total_cells)

        """
        ##### for test purpose;
        ##### draw at each cell it's row and column number
        cx, cy = 0, 0
        for x in col_values:
            cx += 1
            for y in row_values:
                cy += 1
                cv.putText(image, str(cx), (x + 5, y + 11), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
                cv.putText(image, str(cy), (x + 5, y + 19), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
        """

        # cv.imwrite('output.png', image)
        ####### YOU CAN SEE WHAT GRABBING
        # cv.imshow("Display window", image)
        # k = cv.waitKey(0)
        #######
    return row_values, col_values


def init_scan():
    ic('INIT SCAN')
    ic('  first scan...')
    # FIRST SCAN - entire screen, coordinates tied to screen
    region = mss.mss().monitors[0]
    row_values, col_values = scan_region(region)
    if not len(row_values+col_values):
        print('Minesweeper not found, exit')
        exit()
    ic('  finish')

    # add pixels to cell size for get entire game field:
    # left - 14, top - 77, right - 18, boottom - 45

    template = cv.imread('pic/closed.png', cv.IMREAD_COLOR)
    h, w = template.shape[:2]

    left = 18
    right = 18
    top = 81
    bottom = 17

    region_x1 = col_values[0] - left
    region_x2 = col_values[-1] + right + w
    region_y1 = row_values[0] - top
    region_y2 = row_values[-1] + bottom + h

    # SECOND RUN - ONLY WITH REGION OF MINESWEEPER
    ic('  second scan...')
    region = (region_x1, region_y1, region_x2, region_y2)
    ic(region)
    row_values, col_values = scan_region(region)
    ic('  finish')
    return row_values, col_values, region


def create_matrix(row_values, col_values, region):
    ic('Start create matrix...')
    num_rows = len(row_values)
    num_cols = len(col_values)

    template = cv.imread('pic/closed.png', cv.IMREAD_COLOR)
    h, w = template.shape[:2]

    matrix = Matrix(num_cols, num_rows)
    table = matrix.table

    # Здесь мы специально меняем Класс, а не экземпляр, чтобы у объектов Cell был доступ к этим свойствам
    Matrix.region_x1, Matrix.region_y1, Matrix.region_x2, Matrix.region_y2 = region


    ##### test
    # with mss.mss() as sct:
    #     screenshot = sct.grab(sct.monitors[0])
    #     raw = np.array(screenshot)
    #     image = cv.cvtColor(raw, cv.COLOR_RGB2BGR)
    #     image = cv.rectangle(image, (matrix.region_x1, matrix.region_y1), (matrix.region_x2, matrix.region_y2), (0, 255, 0))
    #     cv.imshow("Display window", image)
    #     k = cv.waitKey(0)
    #### end test

    for x, coordx in enumerate(col_values):         # cell[столбец][строка]
        for y, coordy in enumerate(row_values):
            c = Cell(x, y, coordx, coordy, w, h)
            table[x][y] = c

    ic('Matrix created.')
    return matrix


if __name__ == '__main__':
    # image = "pic/closed.png"
    row_values, col_values, region = init_scan()
    matrix = create_matrix(row_values, col_values, region)
    # print(matr.table)

    # matrix.table[0][0].click()

    x = random.randrange(matrix.len_x)
    y = random.randrange(matrix.len_y)
    matrix.table[x][y].click('left')
    matrix.update()

    while not matrix.face_is_fail():
        bombs, clears = solve(matrix)
        ic(bombs)

        for bomb in bombs:
            matrix.table[bomb[0]][bomb[1]].click('right')
        for clear in clears:
            matrix.table[clear[0]][clear[1]].click('left')

        matrix.update()
        matrix.display()

        if not bombs and not clears:
            break
