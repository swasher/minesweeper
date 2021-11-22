import random
import time
import sys
import os
import cv2 as cv
import mss
import numpy as np
import pickle
import timeit
import secrets
from datetime import datetime
from icecream import ic
ic.configureOutput(outputFunction=lambda *a: print(*a, file=sys.stderr))

from config import config
from util import pause
from util import cell_coordinates
from asset import patterns
from asset import Asset
from util import search_pattern_in_image
from matrix import Matrix

from solver import solver_R1
from solver import solver_R1_corner
from solver import solver_R1_smart
from solver import solver_B1
from solver import solver_E1
from solver import solver_E2
from solver import solver_B2
from solver import solver_B1E1
from solver import solver_human
from solver import solver_noguess
from solver import noguess_finish



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
and second number - it is COLUMN: table[row, col]  
 
For example, [1, 2] - it's second row and third column.

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
    print('Try finding board...')
    with mss.mss() as sct:
        region = mss.mss().monitors[0]
        screenshot = sct.grab(region)
        raw = np.array(screenshot)
    image = cv.cvtColor(raw, cv.COLOR_BGRA2BGR)
    precision = 0.8

    cells = search_pattern_in_image(pattern.closed.raster, image, precision)
    cells_coord_x, cells_coord_y = cell_coordinates(cells)

    if not len(cells_coord_x + cells_coord_y):
        print(' - not found, exit')
        exit()
    print(f' - found, {len(cells_coord_x)}x{len(cells_coord_y)}')

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
        matrix.lastclicked = cell
        cell.click(button)


def do_strategy(strategy):
    """
    Обертка для выполнения "стратегии" - после того как алгоритм `strategy` найдет, что нажимать, эта функция нажимает
    нужные клетки, обновляет matrix, пишет лог и так далее.

    Результат работы любой стратегии - список клеток, которые нужно нажать правой или левой кнопкой.

    :param strategy: [function] Одна из функий из модуля solve, напр. можно передать сюда стратегию solver_E1 или solver_R1
    :return: have_a_move: [boolean] - True, если стратегия выполнила ходы
    :return: win_or_fail: [string] - 'win', если ход закончил игру выигрышем, 'fail' если ход закончил игру проигрышем, и None если игра после хода не закончилась
    """

    # TODO Сделать, чтобы можно было прервать процесс с клавиатуры
    # TODO Пример, как это можно реализовать через потоки - keyboard_in_thread.py

    name = strategy.__name__

    # debug
    # if name in ['solver_R1', 'solver_B2', 'solver_E2'] and len(matrix.get_open_cells()) > 15:
    #     print(name)

    # if move is random click - save board to PNG and Pickle file (board object)
    # todo move it to separate file
    if name == 'solver_R1' and config.save_game_R1 and len(matrix.get_open_cells()) > 15:
        random_string = secrets.token_hex(2)
        date_time_str = datetime.now().strftime("%d-%b-%Y--%H.%M.%S.%f")
        picklefile = 'obj.pickle'
        image_file = 'image.png'
        dir = 'game_R1_' + date_time_str + '_' + random_string
        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(os.path.join(dir, picklefile), 'wb') as outp:
            pickle.dump(matrix, outp, pickle.HIGHEST_PROTOCOL)

        image = matrix.get_image()
        cv.imwrite(os.path.join(dir, image_file), image)

    win_or_fail = None
    # print(f'\nCalc {name} strategy')

    cells, button = strategy(matrix)
    have_a_move = bool(len(cells))
    if have_a_move:
        # print(f'- do strategy')
        # print(f'- click {button} on:', cells)

        # debug
        # if config.turn_by_turn:
        #     for c in cells:
        #         c.mark_cell_debug()
        #     input("Press Enter to mouse moving")

        if config.noflag and name in ['solver_B1', 'solver_B2', 'solver_E1B1']:
            # в этом режиме мы должны только "запомнить", т.е. пометить в матрице, где флаги,
            # вместо того, чтобы реально отмечать их на поле
            for cell in cells:
                cell.set_flag()
        else:
            clicking_cells(cells, button)

        matrix.update()
        # matrix.display()

        if button in ['left', 'both']:
            # Если в strategy использовалась правая кнопка, т.е. ставились флажки, то игра не могла закончиться.
            # Проверяем только если использовалась левая - т.е. открывались клетки.
            if matrix.you_win:
                win_or_fail = 'win'
            if matrix.you_fail:
                win_or_fail = 'fail'
    else:
        # print('- pass strategy')
        pass

    if name == 'noguess_finish':
        win_or_fail = 'fail'
    return have_a_move, win_or_fail


def recusive_strategy(i):
    have_a_move, win_or_fail = do_strategy(strategies[i])
    if win_or_fail:
        return win_or_fail
    if have_a_move:
        return recusive_strategy(0)
    else:
        i += 1
        return recusive_strategy(i)


def recursive_wrapper(strategies):
    global matrix
    if config.noguess:  # режим 'без отгадывания'
        strategies.remove(solver_R1)
        strategies.append(noguess_finish)
        matrix.update()

    need_win = config.need_win_parties
    need_total = config.need_total_parties
    win = 0
    total = 0

    while True:
        print('-new round')
        i = 0
        before = datetime.now()
        if config.noguess:
            do_strategy(solver_noguess)
        win_or_fail = recusive_strategy(i)
        after = datetime.now()

        total += 1
        if win_or_fail == 'win':
            win += 1
        elif win_or_fail == 'fail':
            pass

        print(f'{win_or_fail} in', (after-before).seconds, 'sec')
        print(f'Total: {total}, win: {win}, fail: {total - win} (need {need_win} win and {need_total} total)\n')

        # пауза примерно `beetwen_games` секунд, если оно не ноль
        if config.beetwen_games:
            t = abs(random.gauss(config.beetwen_games, 2))
            pause(t)

        contin = (bool(need_win) and win < need_win) or (bool(need_total) and total < need_total)
        if not contin:
            break
        matrix.reset()
        if config.arena:
            col_values, row_values, region = find_board(patterns, Asset)
            matrix = Matrix(row_values, col_values, region)
        matrix.update()

    print('\n=============')
    print(f'TOTALS: {total}')
    print(f'WIN: {win}')
    print(f'FAIL: {total-win}')
    print(f'WIN PERCENT: {win*100/total:.2f}')


if __name__ == '__main__':
    col_values, row_values, region = find_board(patterns, Asset)
    matrix = Matrix(row_values, col_values, region)

    # matrix.bomb_counter2()

    # debug - test perfomance
    # print(timeit.Timer(matrix.bomb_counter2).timeit(number=100))

    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_R1]
    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_R1_corner]
    strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_R1_smart]
    # strategies = [solver_B1E1, solver_B2, solver_E2, solver_R1]

    config.human = False
    if config.human:  # режим 'human'
        strategies.remove(solver_R1)
        strategies.append(solver_human)
        matrix.update()

    recursive_wrapper(strategies)


# самое-самое начало
# some logic
#
# - самое начало
# выполняем R1 один раз
# - начало
# выполняем B1, если ход есть выполняем и идем в начало, иначе продолжаем
# выполняем E1, если ход есть выполняем и идем в начало, иначе продолжаем
# выполняем B2, если ход есть выполняем и идем в начало, иначе продолжаем
# выполняем E2, если ход есть выполняем и идем в начало, иначе продолжаем
# ..... E3, B3 и т.д
# идем в самое начало
#
# на каждом ходе нужно проверить Game Over или You Win. Если да, идем в самое-самое начало.



