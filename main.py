import random

import cv2 as cv
import mss
import numpy as np
from icecream import ic

import solve
from util import scan_region
from patterns import patterns
from matrix import Matrix

from solve import solver_B1
from solve import solver_E1
from solve import solver_R1

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



def find_board(pattern):
    """
    Находит поле сапера
    :return: row, cols - кол-во столбцов и строк в поле; region - координаты сапера на экране, первая пара - верхний левый угол, вторая пара - нижний правый угол
    """
    ic('FINDING BOARD')
    ic('  first scan...')
    # FIRST SCAN - entire screen, coordinates tied to screen
    region = mss.mss().monitors[0]
    cells_coord_x, cells_coord_y = scan_region(region, pattern.closed.raster)
    if not len(cells_coord_x+cells_coord_y):
        print('Minesweeper not found, exit')
        exit()
    ic('  finish')

    template = pattern.closed.raster
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
    cells_coord_x, cells_coord_y = scan_region(region, pattern.closed.raster)
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
        image = cv.cvtColor(raw, cv.COLOR_BGRA2BGR)
        image = cv.rectangle(image, (matrix.region_x1, matrix.region_y1), (matrix.region_x2, matrix.region_y2), (0, 255, 0))
        cv.imshow("Display window", image)
        k = cv.waitKey(0)


def clicking_cells(cells, button):
    for cell in cells:
        cell.click(button)


def do_strategy(strategy):
    """
    Обертка для выполнения "стратегии" - после того как алгоритм найдет, что нажимать, эта функция нажимает
    нужные клетки, обновляет matrix, пишет лог и так далее.

    Результат работы любой стратегии - список клеток, которые нужно нажать правой или левой кнопкой.

    :param strategy: Одна из функий из модуля solve, напр. можно передать сюда стратегию solver_E1 или solver_R1
    :return:
    """

    # TODO Сделать, чтобы можно было прервать процесс с клавиатуры

    name = strategy.__name__
    print(f'\nCalc {name} strategy')

    cells, button = strategy(matrix)
    have_a_move = bool(len(cells))
    if have_a_move:
        print(f'- do strategy')
        print(f'- click {button} on cells:', cells)
        # input("Press Enter to mouse moving")
        clicking_cells(cells, button)
        matrix.update()
        matrix.display()
        matrix.check_game_over()
    else:
        print('- pass strategy')
    return have_a_move


if __name__ == '__main__':

    # TODO я хочу, чтобы можно было так делать:
    # TODO if bomb in matrix:
    # TODO или, если у нас есть array of cells
    # TODO if bomb in array

    row_values, col_values, region = find_board(patterns)
    matrix = Matrix(row_values, col_values, region, patterns)

    have_a_move_B1 = True
    have_a_move_E1 = True
    do_random = True

    # matrix.update()
    # matrix.check_game_over()

    while do_random:
        do_strategy(solver_R1)

        have_a_move_B1 = True
        while have_a_move_B1:
            have_a_move_B1 = do_strategy(solver_B1)

            have_a_move_E1 = True
            while have_a_move_E1:
                have_a_move_E1 = do_strategy(solver_E1)
