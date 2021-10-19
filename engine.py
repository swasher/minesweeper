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

"""
RULES FOR COORDINATES
Board matrix represented by array of arrays, ie
[[· · · · · · · · ·], [· · · 1 · · · · ·], [· · · · · · · · ·], [· · · · · · · · ·], [· · 3 4 2 2 · · ·], [· · · 1 ⨯ 1 · · ·], [· 2 1 1 ⨯ 1 · · ·], [· 1 ⨯ ⨯ ⨯ 1 · · ·], [· 1 ⨯ ⨯ ⨯ 1 · · ·]]

or

[[· · · · · · · · ·], 
 [· · · 1 · · · · ·], 
 [· · · · · · · · ·], 
 [· · · · · · · · ·], 
 [· · 3 4 2 2 · · ·], 
 [· · · 1 ⨯ 1 · · ·], 
 [· 2 1 1 ⨯ 1 · · ·], 
 [· 1 ⨯ ⨯ ⨯ 1 · · ·], 
 [· 1 ⨯ ⨯ ⨯ 1 · · ·]]

First number - its OUTER list, 
second number - INNER list

So first numer - it'a apply to line number or ROW
and second number - it is COLUMN 

For example, [1, 2] - it's second row and third column.

In terms of X:Y coordinates, axis X is vertically, and Y is horizontally.
Alse X - its ROWS
and  Y - its COLUMNS

So [1, 2] in xy coord will be (x, y) = (1, 2):

   y0  y1  y2
x0
x1
x2 


"""



def scan_region(region):
    """
    :param region
    Возвращает два списка row_values и col_values. Начало координат - верх лево.
    :return: cells_coord_x - список координаты по оси X для каждого столбца (в пикселях относительно верха лева экрана)
    :return: cells_coord_y - анал. по оси Y
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

        cells_coord_y = []
        cells_coord_x = []
        for i in cells:
            cells_coord_x.append(i[0])
            cells_coord_y.append(i[1])

        # Эти два списка - искомые координаты ячеек
        cells_coord_y = sorted(list(set(cells_coord_y)))  # кол-во соотв. кол-ву строк; координаты строк сверху вниз по Y
        cells_coord_x = sorted(list(set(cells_coord_x)))  # кол-во соотв. кол-ву столбцов; координаты столбцов слева направо по X

        num_rows = len(cells_coord_y)
        num_cols = len(cells_coord_x)
        total_cells = len(cells_coord_y) * len(cells_coord_x)

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
    return cells_coord_y, cells_coord_x


def find_board():
    """
    Находит поле сапера
    :return: row, cols - кол-во столбцов и строк в поле; region - координаты сапера на экране, первая пара - верхний левый угол, вторая пара - нижний правый угол
    """
    ic('FINDING BOARD')
    ic('  first scan...')
    # FIRST SCAN - entire screen, coordinates tied to screen
    region = mss.mss().monitors[0]
    cells_coord_x, cells_coord_y = scan_region(region)
    if not len(cells_coord_x+cells_coord_y):
        print('Minesweeper not found, exit')
        exit()
    ic('  finish')

    template = cv.imread('pic/closed.png', cv.IMREAD_COLOR)
    h, w = template.shape[:2]

    # add pixels to cells size for get entire game board:
    # left - 18, top - 81, right - 18, boottom - 17
    left = 18
    right = 18
    top = 81
    bottom = 17

    region_x1 = cells_coord_y[0] - left
    region_x2 = cells_coord_y[-1] + right + w
    region_y1 = cells_coord_x[0] - top
    region_y2 = cells_coord_x[-1] + bottom + h

    # SECOND RUN - ONLY WITH REGION OF MINESWEEPER
    # coordinates cells_coord_x, cells_coord_y tied to minesweeper board
    ic('  second scan...')
    region = (region_x1, region_y1, region_x2, region_y2)
    cells_coord_y, cells_coord_x = scan_region(region)
    ic('  finish')
    return cells_coord_x, cells_coord_y, region


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

    for x, coordx in enumerate(col_values):         # cell[строка][столбец]
        for y, coordy in enumerate(row_values):
            c = Cell(x, y, coordx, coordy, w, h)
            table[x][y] = c


    ic('Matrix created.')
    return matrix


if __name__ == '__main__':
    # image = "pic/closed.png"
    rows, cols, region = find_board()
    matrix = create_matrix(rows, cols, region)
    # print(matr.table)

    # matrix.table[0][0].click()

    x = random.randrange(matrix.len_x)
    y = random.randrange(matrix.len_y)
    # matrix.table[x][y].click('left')
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
