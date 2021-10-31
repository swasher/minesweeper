import time
import sys
import cv2 as cv
import mss
import numpy as np
from icecream import ic
ic.configureOutput(outputFunction=lambda *a: print(*a, file=sys.stderr))

from config import config
from util import scan_image
from patterns import patterns
from patterns import Asset
from matrix import Matrix

from solve import solver_R1
from solve import solver_B1
from solve import solver_E1

from solve import solver_B2
from solve import solver_E2


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


def find_board(pattern, asset):
    """
    Находит поле сапера

    :param pattern: объект Pattern, который содержит изображения клеток; мы будем искать на экране закрытую клетку (pattern.closed)
    :param asset: класс (не инстанс!) Asset, в котором содержится информация о "доске" - а именно размер полей в пикселях,
            от клеток до края "доски". Именно это поле (region), а не весь экран, мы в дальнейшем будем "сканировать".
    :return cells_coord_x: [array of int] Координаты строк
    :return cells_coord_y: [array of int] Координаты столбцов
    :return region: [x1, y1, x2, y2] координаты доски сапера на экране, первая пара - верхний левый угол, вторая пара - нижний правый угол
    """
    ic('Try finding board...')
    with mss.mss() as sct:
        region = mss.mss().monitors[0]
        screenshot = sct.grab(region)
        raw = np.array(screenshot)
    image = cv.cvtColor(raw, cv.COLOR_BGRA2BGR)
    cells_coord_x, cells_coord_y = scan_image(image, pattern.closed.raster)

    if not len(cells_coord_x + cells_coord_y):
        print(' - not found, exit')
        exit()
    ic(' - found')

    template = pattern.closed.raster
    h, w = template.shape[:2]

    # Это поля "игрового поля" в дополнение к самим клеткам в пикселях
    left = asset.border['left']
    right = asset.border['right']
    top = asset.border['top']
    bottom = asset.border['bottom']

    region_x1 = cells_coord_x[0] - left
    region_x2 = cells_coord_x[-1] + right + w
    region_y1 = cells_coord_y[0] - top
    region_y2 = cells_coord_y[-1] + bottom + h

    region = (region_x1, region_y1, region_x2, region_y2)

    # Делаем коррекцию координат, чтобы они было относительно доски, а не экрана.
    cells_coord_x = [x-region_x1 for x in cells_coord_x]
    cells_coord_y = [y-region_y1 for y in cells_coord_y]

    return cells_coord_x, cells_coord_y, region


def draw():
    """
    TODO ДОПИЛИТЬ ФУНКЦИЮ, ЧТОБЫ ДЕЛАТЬ ДЕБАГ-КАРТИНКИ
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

    :param strategy: [function] Одна из функий из модуля solve, напр. можно передать сюда стратегию solver_E1 или solver_R1
    :return: have_a_move: [boolean] - True, если стратегия выполнила ходы
    """

    # TODO Сделать, чтобы можно было прервать процесс с клавиатуры

    name = strategy.__name__
    print(f'\nCalc {name} strategy')

    cells, button = strategy(matrix)
    have_a_move = bool(len(cells))
    if have_a_move:
        print(f'- do strategy')
        print(f'- click {button} on cells:', cells)

        # if config.turn_by_turn:
        #     input("Press Enter to mouse moving")
        clicking_cells(cells, button)

        # This is very important setting! After click, website has a lag for refresh game board.
        # If we do not waiting at this point, we do not see any changes after mouse click.
        time.sleep(config.LAG)
        matrix.update()
        matrix.display()
        if matrix.you_win():
            print('You win!')
            sys.exit()
        if matrix.you_fail():
            print('Game over!')
            sys.exit()
    else:
        print('- pass strategy')
    if name == 'solver_R1':
        have_a_move = False
    return have_a_move


if __name__ == '__main__':

    # ===== DEBUG

    # row_values, col_values, region = find_board(patterns)
    # matrix = Matrix(row_values, col_values, region, patterns)
    # matrix.update()
    # move = True
    # while move:
    #     move = do_strategy(solver_E2)
    #     input('next turn')
    # sys.exit()

    # ===== END DEBUG


    # TODO я хочу, чтобы можно было так делать:
    # TODO if bomb in matrix:
    # TODO или, если у нас есть array of cells
    # TODO if bomb in array

    col_values, row_values, region = find_board(patterns, Asset)
    matrix = Matrix(row_values, col_values, region, patterns)

    # for col in matrix.table.wi

    have_a_move_B1 = True
    have_a_move_E1 = True
    do_random = True



    WIN = 5

    while do_random:
        # input('lets R1...')
        do_strategy(solver_R1)

        have_a_move_B2 = True
        # input('lets B2...')
        while have_a_move_B2:
            have_a_move_B2 = do_strategy(solver_B2)

            have_a_move_E2 = True
            # input('lets E2...')
            while have_a_move_E2:
                have_a_move_E2 = do_strategy(solver_E2)

                have_a_move_B1 = True
                while have_a_move_B1:
                    have_a_move_B1 = do_strategy(solver_B1)

                    have_a_move_E1 = True
                    while have_a_move_E1:
                        have_a_move_E1 = do_strategy(solver_E1)

    pass

    # strat = [solver_E2, solver_B2, solver_E1, solver_B1, solver_R1]
    # strat = [solver_R1, solver_B1, solver_E1, solver_B2, solver_E2]



