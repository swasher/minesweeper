import sys
import time
import threading
import random
import queue
from pynput.keyboard import Key, Listener
from icecream import ic
import ctypes

from config import config

from core.screen import ScreenMatrix
from core import Action
from core import Cell
from core.screen import find_board

from utils import Color
from utils import controlled_pause

from solver import solver_R1
from solver import solver_R1_corner
from solver import solver_R1_smart
from solver import solver_B1
from solver import solver_E1
from solver import solver_E2
from solver import solver_B2
from solver import solver_B1E1
from solver import solver_gauss
from solver import solver_noguess

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
a  row0
x  row1
i  row2 
s
0

"""

def initialize():
    global last_click_time
    last_click_time = time.perf_counter()

    global q
    q = queue.Queue()

#
# Вычисляется время между реальным кликами. Если нет искуственных пауз - это время, ушедшее на
# вычисления.
#
def clicking_cells(cells: [Cell], action: Action):
    global last_click_time

    for cell in cells:
        matrix.lastclicked = cell
        if config.print_time_between_clicks:
            current_time = time.perf_counter()
            print(f'click delay: {current_time - last_click_time:.3f}\n')
            last_click_time = current_time
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
            print(f'{name}: {cells} -> {action.__str__()}')
        else:
            print(f'{name}: pass')

    # matrix.display()

    if have_a_move:

        # debug
        print(config.turn_by_turn)
        print(bool(config.turn_by_turn))
        if config.turn_by_turn:
            for c in cells:
                c.mark_cell_debug(Color.green)
            print("Any key for continue, 's' for save")
            while True:
                time.sleep(0.05)
                if not q.empty():
                    message = q.get()
                    if message == 'save':
                        matrix.save()
                        print('Matrix saved')
                    break

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
        # DEBUG - POINT AFTER EACH CLICK
        # --------------------------------

        matrix.display()

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

        if config.no_guess:  # режим 'первый ход без отгадывания'
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
            controlled_pause(t)

        contin = (bool(need_win) and win < need_win) or (bool(need_total) and total < need_total)
        if not contin:
            break
        matrix.click_smile()
        if config.arena:
            # TODO find_board принимает только 1 аргумент!!!!
            col_values, row_values, region = find_board()
            matrix = ScreenMatrix(row_values, col_values, region)

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
    elif key.char.lower() == 's':
        q.put('save')
    else:
        q.put('continue')


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


# Если мы используем слушатель клавиатуры, то дебаг становится нереальным - кнопки перехватываются.
# Поэтому идея была такая, чтобы этот режим можно было включить и выключить.
# Но это нужно допилить.
use_keyboard_listener = True

if __name__ == '__main__':

    initialize()

    if use_keyboard_listener:
        listener = Listener(on_press=on_press)
        listener.start()  # Запускаем слушатель в отдельном потоке

    col_values, row_values, region = find_board()

    matrix = ScreenMatrix(row_values, col_values, region)
    print('Matrix creted:')
    matrix.display()



    # Список стратегий не передается как параметр, функции обращаются к нему как к внешней переменной
    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_R1]
    # strategies = [solver_B1, solver_E1, solver_R1]

    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_R1_corner]
    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_human]
    # strategies = [solver_B1, solver_E1, solver_B2, solver_E2, solver_R1_smart]
    # strategies = [solver_gauss, solver_R1]

    # рабочий
    strategies = [solver_B1E1, solver_B2, solver_E2, solver_R1_smart]


    config.human = False
    if config.human:  # режим 'human'
        strategies.remove(solver_R1)
        strategies.append(solver_human)
        matrix.update()

    # recursive_wrapper - это основная точка входа в запуск стратегий, теперь выполняется в отдельном потоке, для того
    # чтобы его можно было остановить по нажатию клавиши
    # recursive_wrapper(strategies)

    if use_keyboard_listener:
        t1 = thread_with_exception('Thread 1')
        t1.start()
        # остановка потока по нажатию Esc выполняется в колбеке on_press(key):
        t1.join()
        listener.stop()
    else:
        recursive_wrapper()
