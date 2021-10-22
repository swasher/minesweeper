import random

import cv2 as cv
import mss
import numpy as np
from icecream import ic

import solve
from patterns import patterns
from cell import Cell
from matrix import Matrix

from solve import solver_B1
from solve import solver_E1

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

"Первая" ось 0 это по строкам, "вторая" - по столбцам
table[строка, столбец]
table[row, col]

        axis 1
       col0  col1  col2
a row0
x row1
i row2 
s
0

"""


def scan_region(region, samplefile):
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
        # for prod
        screenshot = sct.grab(region)
        raw = np.array(screenshot)
        image = cv.cvtColor(raw, cv.COLOR_RGB2BGR)

        # for dev
        # image = cv.imread('pic/test_big.png', cv.IMREAD_COLOR)

        template = cv.imread(samplefile, cv.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError('Image file not found: {}'.format(image))

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

        def collapse_coords(coords):
            # input list [1, 10, 10, 10, 20, 30, 40, 50, 50, 50]

            # set убирает дубликаты
            collapsed = sorted(list(set(cells_coord_y)))
            return collapsed

        # Эти два списка - искомые координаты ячеек. Убираем из них дубликаты при помощи set()
        cells_coord_y = collapse_coords(cells_coord_y)  # кол-во соотв. кол-ву строк; координаты строк сверху вниз по Y
        cells_coord_x = sorted(list(set(cells_coord_x)))  # кол-во соотв. кол-ву столбцов; координаты столбцов слева направо по X

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

    # TODO тут опять непонятные x y
    return cells_coord_y, cells_coord_x


def find_board(asset):
    """
    Находит поле сапера
    :return: row, cols - кол-во столбцов и строк в поле; region - координаты сапера на экране, первая пара - верхний левый угол, вторая пара - нижний правый угол
    """
    ic('FINDING BOARD')
    ic('  first scan...')
    # FIRST SCAN - entire screen, coordinates tied to screen
    region = mss.mss().monitors[0]
    cells_coord_x, cells_coord_y = scan_region(region, asset.closed.filename)
    if not len(cells_coord_x+cells_coord_y):
        print('Minesweeper not found, exit')
        exit()
    ic('  finish')

    template = cv.imread(asset.closed.filename, cv.IMREAD_COLOR)
    h, w = template.shape[:2]

    # add pixels to cells size for get entire game board:
    # left - 18, top - 81, right - 18, boottom - 17
    # TODO эти параметры должны быть привязаны к ассету
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
    cells_coord_x, cells_coord_y = scan_region(region, asset.closed.filename)
    ic('  finish')
    return cells_coord_x, cells_coord_y, region


def draw():
    """
    ДОПИЛИТЬ ФУНКЦИЮ, ЧТОБЫ ДЕЛАТЬ ДЕБАГ-КАРТИНКИ
    :return: 
    """
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0])
        raw = np.array(screenshot)
        image = cv.cvtColor(raw, cv.COLOR_RGB2BGR)
        image = cv.rectangle(image, (matrix.region_x1, matrix.region_y1), (matrix.region_x2, matrix.region_y2), (0, 255, 0))
        cv.imshow("Display window", image)
        k = cv.waitKey(0)

# TODO move it!
def mark_cells(bombs, empties):
    for cell in bombs:
        ic(bombs)
        cell.setflag()
    for cell in empties:
        cell.setclear()


def do_strategy(strategy):
    name = strategy.__name__
    print(f'Calc {name} strategy')
    bombs, empties = strategy(matrix)
    have_a_move = len(bombs + empties)
    if have_a_move:
        print(f'- do strategy')
        print('- Bombs:', bombs, 'Empty:', empties)
        mark_cells(bombs, empties)
        matrix.update()
        matrix.display()
    else:
        print('- pass')
    return have_a_move


if __name__ == '__main__':

    row_values, col_values, region = find_board(patterns)
    matrix = Matrix(row_values, col_values, region, patterns)


    have_a_move_B1 = True
    have_a_move_E1 = True
    do_random = True

    while not matrix.face_is_fail:

        have_a_move_E1 = True
        while have_a_move_E1:

            have_a_move_B1 = True
            while have_a_move_B1:

                do_random = True
                while do_random:

                    print('do R1 strategy')
                    bombs, empties = solve.solver_R1(matrix)
                    mark_cells(bombs, empties)
                    matrix.update()
                    matrix.display()
                    do_random = False

                have_a_move_B1 = do_strategy(solver_B1)

            have_a_move_E1 = do_strategy(solver_E1)

    # input("Press Enter to continue...")

        # if not bombs and not empties:
        #     break
