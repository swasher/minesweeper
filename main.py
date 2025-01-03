import random
import time
import sys
import os
import cv2 as cv
import mss
import numpy as np
from pynput.keyboard import Key, Listener
import timeit
from datetime import datetime
from icecream import ic
import win32gui
import win32api

from config import config
from util import pause
from util import cell_coordinates

import threading
import ctypes
import time

import asset
from board import board

from util import search_pattern_in_image
from matrix import Matrix
from classes import Action
import save_load

from solver import solver_R1
from solver import solver_R1_corner
from solver import solver_R1_smart
from solver import solver_B1
from solver import solver_E1
from solver import solver_E2
from solver import solver_B2
from solver import solver_B1E1
from solver import solver_human, solver_human_almost_work
from solver import solver_gauss
from solver import solver_noguess

from cell import Cell

ic.configureOutput(outputFunction=lambda *a: print(*a, file=sys.stderr))

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


def find_board(closedcell):
    """
    Находит поле сапера

    :param board: global variable
    :param pattern: объект Pattern, который содержит изображения клеток; мы будем искать на экране закрытую клетку (pattern.closed)
    :param asset: класс (не инстанс!) Asset, в котором содержится информация о "доске" - а именно размер полей в пикселях,
            от клеток до края "доски". Именно это поле (region), а не весь экран, мы в дальнейшем будем "сканировать".
    :return cells_coord_x: [array of int] Координаты строк (верхних левых углов клеток, относительно доски)
    :return cells_coord_y: [array of int] Координаты столбцов (верхних левых углов клеток, относительно доски)
    :return region: [x1, y1, x2, y2] координаты доски сапера на экране, первая пара - верхний левый угол, вторая пара - нижний правый угол. Включает всю доску с полями вокруг.
    """
    print('Try finding board...')
    with mss.mss() as sct:
        region = mss.mss().monitors[0]
        screenshot = sct.grab(region)
        raw = np.array(screenshot)
    image = cv.cvtColor(raw, cv.COLOR_BGRA2BGR)
    precision = 0.8

    cells = search_pattern_in_image(closedcell.raster, image, precision)
    cells_coord_x, cells_coord_y = cell_coordinates(cells)

    if not len(cells_coord_x + cells_coord_y):
        print(' - not found, exit')
        exit()
    print(f' - found, {len(cells_coord_x)}x{len(cells_coord_y)}')

    template = closedcell.raster
    h, w = template.shape[:2]

    # Это поля "игрового поля" в дополнение к самим клеткам в пикселях
    left = board.border['left']
    right = board.border['right']
    top = board.border['top']
    bottom = board.border['bottom']

    region_x1 = cells_coord_x[0] - left
    region_x2 = cells_coord_x[-1] + right + w
    region_y1 = cells_coord_y[0] - top
    region_y2 = cells_coord_y[-1] + bottom + h

    region = (region_x1, region_y1, region_x2, region_y2)

    # Делаем коррекцию координат, чтобы они было относительно доски, а не экрана.
    cells_coord_x = [x-region_x1 for x in cells_coord_x]
    cells_coord_y = [y-region_y1 for y in cells_coord_y]

    DEBUG_DRAW_RECTANGLE = False
    if DEBUG_DRAW_RECTANGLE:
        dc = win32gui.GetDC(0)
        red = win32api.RGB(255, 0, 0)
        win32gui.SetPixel(dc, 0, 0, red)  # draw red at 0,0
        win32gui.Rectangle(dc, region_x1, region_y1, region_x2, region_y2)

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

#
# Вычисляется время между реальным кликами. Если нет искуственных пауз - это время, ушедшее на
# вычисления.
#
import queue
q = queue.Queue()
q.put(time.perf_counter())
def clicking_cells(cells: [Cell], action: Action):
    for cell in cells:
        matrix.lastclicked = cell
        n = time.perf_counter()
        prev = q.get()
        # print('real sec:', n-prev, '\n')
        q.put(n)
        cell.click(action.button)


def do_strategy(strategy):
    """
    Результат работы любой Стратегии - список клеток, которые нужно нажать правой или левой кнопкой.

    Эта функция - обертка для выполнения "стратегии", по результатам выполнения Стретегии она нажимает
    нужные клетки, обновляет matrix, пишет лог и так далее.

    :param strategy: [function] Одна из функий из модуля solve, напр. можно передать сюда стратегию solver_E1 или solver_R1
    :return: have_a_move: [boolean] - True, если стратегия выполнила ходы
    :return: win_or_fail: [string] - 'win', если ход закончил игру выигрышем, 'fail' если ход закончил игру проигрышем, и None если игра после хода не закончилась
    """

    name = strategy.__name__

    win_or_fail = None

    cells, action = strategy(matrix)

    # смотрим, нашла ли Стратегия доступные для выполнения ходы
    have_a_move = bool(len(cells))

    DEBUG_PRINT_EVERY_MOVE = False
    if DEBUG_PRINT_EVERY_MOVE:
        if have_a_move:
            print(f'move: {name}: [{action.name}] {cells}')
        else:
            print(f'move: {name}: [{action}] pass')

    if have_a_move:
        # debug
        # if config.turn_by_turn:
        #     for c in cells:
        #         c.mark_cell_debug()
        #     input("Press Enter to mouse moving")

        # --------------------------------
        # В ЭТОЙ ТОЧКЕ МЫ ДОЛЖНЫ СДЕЛАТЬ ЗАДЕРЖКУ, ИМИТИРУЯ "ДУМАНИЕ" ЧЕЛОВЕКА
        # ПРОБЛЕМА - клики могут быть набором, но в таком случае можно решить, что внутри набора нет дополнительной задержки.
        # что мы можем включить в рассчеты:
        # - мы уже знаем, где будет следующий клик, - и насколько он далеко от текущей позиции.
        #     если далеко, то, вероятно, человеку нужно было время для размышления.
        # - если есть большие цифры - 5,6, человеку нужно больше времни чтобы подумать
        # - если была применена стратегия E2 или B2 - она требовала больше времени на размышления (чем Е1 и Б1)
        # - отсутствие ходов - заставляет человека думать
        # - на время думания мы можем не просто останавливать игру, а мадленно перемещать мышь ближе к району следующего клика
        # - кроме того, нужно ввести задержку между нажатием и отпусканием кнопки мыши - человек не делает это мгновенно.
        # --------------------------------

        human_thinking = 0
        time.sleep(human_thinking)

        if config.noflag and action == Action.set_flag:
            # в этом режиме мы должны только "запомнить", т.е. пометить в матрице, где флаги,
            # вместо того, чтобы реально отмечать их на поле
            for cell in cells:
                cell.set_flag()
        else:
            clicking_cells(cells, action)

        matrix.update()
        # matrix.display()

        # --------------------------------
        # DEBUG PAUSE HERE AFTER EACH MOVE
        # --------------------------------

        # DEBUG
        # мы можем после хода сохранить состояние игры в папку
        # if name == 'solver_E2':
        #     matrix.save()

        if action in [Action.open_cell, Action.open_digit]:
            # Если в strategy мы помечали бомбы, то игра не могла закончиться.
            # Проверяем только если открывались клетки.
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
    move_happened, win_or_fail = do_strategy(strategies[i])
    if win_or_fail:
        return win_or_fail
    if move_happened:
        return recusive_strategy(0)
    else:
        i += 1
        return recusive_strategy(i)


def recursive_wrapper():
    """
    Самая внешняя обертка, которая работает над "играми" - запускает, подсчитывает, останавливает, etc.
    :param strategies:
    :return:
    """
    global matrix

    need_win = config.need_win_parties
    need_total = config.need_total_parties
    win = 0
    total = 0

    while True:
        print('-new round')
        i = 0
        before = time.perf_counter()

        if config.noguess:  # режим 'первый ход без отгадывания'
            do_strategy(solver_noguess)
            matrix.update()

        win_or_fail = recusive_strategy(i)
        after = time.perf_counter()

        total += 1
        if win_or_fail == 'win':
            win += 1
        elif win_or_fail == 'fail':
            pass

        print(f'{win_or_fail} in', after-before, 'sec')
        print(f'Total: {total}, win: {win}, fail: {total - win} (need {need_win} win and {need_total} total)\n')

        # пауза примерно `seconds_beetwen_games` секунд, если оно не ноль (с разбросом sigma=1.5)
        if config.seconds_beetwen_games:
            t = abs(random.gauss(config.seconds_beetwen_games, 1.5))
            pause(t)

        contin = (bool(need_win) and win < need_win) or (bool(need_total) and total < need_total)
        if not contin:
            break
        matrix.reset()
        if config.arena:
            # TODO find_board принимает только 1 аргумент!!!!
            col_values, row_values, region = find_board(asset.closed, board)
            matrix = Matrix()
            matrix.initialize_from_screen(row_values, col_values, region)
        matrix.update()

    print('\n=============')
    print(f'TOTALS: {total}')
    print(f'WIN: {win}')
    print(f'FAIL: {total-win}')
    print(f'WIN PERCENT: {win*100/total:.2f}')


def on_press(key):
    # print(f'pressed {key}')
    if key == Key.esc:
        print('EXIT!!!')
        listener.stop()
        t1.raise_exception()



class thread_with_exception(threading.Thread):
    """
    Это обертка для основного процесса recursive_wrapper().
    В другом, параллельном, потоке запускается слушатель клавиатуры.
    Нужно для того, чтобы мы могли по нажатию Esc остановить игру (убить этот поток).
    """

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        recursive_wrapper()

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')



if __name__ == '__main__':

    listener = Listener(on_press=on_press)
    listener.start()  # Запускаем слушатель в отдельном потоке

    col_values, row_values, region = find_board(asset.closed)
    matrix = Matrix()
    matrix.initialize_from_screen(row_values, col_values, region)

    # кусочек, тестируюший распознавание кол-во бомб, написанное вверху слева на поле.
    # bombs = matrix.bomb_qty(0.87)
    # print(bombs)
    # exit()

    # x = 1.0
    # while x > 0.7:
    #     bombs = matrix.bomb_qty(x)
    #     if bombs == 10:
    #         print(f"{x:.3f}", bombs)
    #     x -= 0.001
    #
    # exit()


    # debug - test perfomance
    # print(timeit.Timer(matrix.bomb_counter2).timeit(number=100))


    # Список стратегий не передается как параметр, функции обращаются к нему как к внешней переменной
    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_R1]
    # strategies = [solver_B1, solver_E1, solver_R1]

    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_R1_corner]
    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_human]
    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_R1_smart]
    # strategies = [solver_gauss, solver_R1]

    # рабочий
    strategies = [solver_B1E1, solver_B2, solver_E2, solver_R1]


    config.human = False
    if config.human:  # режим 'human'
        strategies.remove(solver_R1)
        strategies.append(solver_human)
        matrix.update()


    # recursive_wrapper - это основная точка входа в запуск стратегий, теперь выполняется в отдельном потоке, для того
    # чтобы его можно было остановить по нажатию клавиши
    # recursive_wrapper(strategies)



    t1 = thread_with_exception('Thread 1')
    t1.start()
    # остановка потока по нажатию Esc выполняется в колбеке on_press(key):
    t1.join()
    listener.stop()

# - самое-самое начало
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



