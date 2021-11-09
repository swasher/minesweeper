import itertools
from random import randrange
import numpy as np
import math
import util
from config import config
from asset import Asset
from icecream import ic



"""
Любой алгоритм должен вернуть список ячеек (или []) и действие с ними (строку 'left' or 'right')

Каждый алгоритм возвращает решения сразу, как только нашел (хотя первоначально была идея возвращать решения
bulk-ом для всей доски, оказалось так не комильфо)
"""


def solver_noguess(matrix):
    """
    Первый ход для no-guess игр.
    Нажимает отмеченную крестиком клетку.
    Этот солвер `должен` вернуть X клетку, если нет, значит что-то пошло не так
    :param matrix:
    :return:
    """
    x_cell = matrix.get_noguess_cell()
    if not len(x_cell):
        raise Exception('Error in solver_noguess function! Не найден крест в режиме NG!!!')
    return x_cell, Asset.open


def noguess_finish(matrix):
    """
    Если не осталось ходов, то нужно закончить игру, чтобы не зацикливалось.
    Применяется в игре без угадываения.
    :return:
    """
    print('No_guess: No more turn')
    return [], ''


def solver_R1(matrix):
    """
    Нажимает рандомную клетку из закрытых.
    TODO Нужно научить считать ВЕРОЯТНОСТИ ДЛЯ КЛЕТОК!!!!!
    :param matrix:
    :return:
    """
    ####### START алгоритм оценки вероятности бомбы в закрытой клетке
    ##
    risktable = matrix.table

    for cell in risktable.flat:
        cell.risk = []

    for digit in matrix.get_digit_cells():
        around_closed = matrix.around_closed_cells(digit)
        for cell in around_closed:
            cell.risk.append(digit.digit / len(around_closed))

    for r in risktable.flat:
        if r.risk:
            r.risk = np.mean(r.risk)
    ##
    ####### END



    cells = matrix.get_closed_cells()
    qty = len(cells)
    random_cell = cells[randrange(qty)]

    # TODO при игре на виенне плохо опознает выигрышный конец

    # if config.turn_by_turn:
    #     ic('------ R1')
    #     ic(random_cell)
    #     random_cell.mark_cell_debug()
    #     input("Press Enter to mouse moving")

    return [random_cell], Asset.open


def solver_B1(matrix):
    """
    B1 - значит ищем Bомбы алгоритомом "один"
    :param matrix:
    :return:

    Алгоритм:
    Проверяем все ячейки с цифрами.
    Если цифра в ячейке равно кол-ву соседних закрытых клеток (включая клетки с флагами),
    ТО все оставшиеся неоткрытые клетки - бомбы
    """
    cells = []
    for cell in matrix.get_digit_cells():
        closed = matrix.around_closed_cells(cell)
        flags = matrix.around_flagged_cells(cell)

        if (cell.digit == len(closed) + len(flags)) and len(closed) > 0:
            # значит во всех closed клетках есть бомбы

            # вариант алгоритма с возвратом первой найденной ячейки
            # можно вернуть одну ячейку
            # return closed, 'right'

            for c in closed:
                cells.append(c)


    # В список cells одна и та же ячейка может попасть несколько раз (при анализе разных "цифр"). Убираем дубликаты.
    cells = util.remove_dup(cells)

    # Алгоритм B1 выдает серию клеток; сортировать их в порядке "близости" на поле, а то он помечает их в хаотичном порядке
    # Сделано довольно топорно - от сортирует в порядке возрастания расстояния от центра достки.
    # В принцепе работает, но по феншую нужно сделать "ближайшее к текущей позиции", а затем к "новой текущей", типа рекурсии
    center_x = matrix.region_x1 + (matrix.region_x2 - matrix.region_x1)/2
    center_y = matrix.region_y1 + (matrix.region_y2 - matrix.region_y1)/2
    cells = sorted(cells, key=lambda c: math.hypot(center_x - c.coordx, center_y - c.coordy))

    # ic('------ B1')
    # for cell in cells:
        # ic(cell)
        # cell.mark_cell_debug()
    # input('wait...')

    return cells, Asset.flag


def solver_E1(matrix):
    """
    E1 значит Empty - ищем потенчиально пустые ячейки алгоритмом "один"

    :param matrix:
    :return solution: list, пустой или содержащий 1 объект Cell
    :return Asset.nearby: string, определяющий кнопку мыши

    Алгоритм:
    Проверяем все ячейки с цифрами.
    Если вокруг ячейки с цифрой такое же кол-во флагов, и вокруг есть закрытые
    ячейки, ТО все закрытые ячейки вокруг являются пустыми.

    Алгоритм сканирует все поле по этому принципу, затем выбирает ту ячейку, у которой максимальное кол-во пустых клеток.

    HINT: Такие ячейки можно "вскрыть" левым или "both" кликом - откроются все вокруг.
    """
    cells = []
    for cell in matrix.get_digit_cells():
        closed = matrix.around_closed_cells(cell)
        flags = matrix.around_flagged_cells(cell)

        if cell.digit == len(flags) and len(closed):
            cell.nearby_closed = len(matrix.around_closed_cells(cell))
            cells.append(cell)

    if cells:
        solution = [max(cells, key=lambda item: item.nearby_closed)]

        # if config.turn_by_turn:
        #     ic('------ E1')
        #     ic(solution)
        #     solution.mark_cell_debug()
    else:
        # если ни у одной клетки нет решения, возвращаем пустой список
        solution = []

    return solution, Asset.nearby


class Root(object):
    ancestor = None # объект Cell - клетка, для которой строился root
    closed = []     # список объектов Cell
    flags = []      # список объектов Flag
    number = 0      # int, цифра, вокруг которой построен "корень"

    def __init__(self, cell, closed, flags):
        self.ancestor = cell
        self.closed = closed
        self.flags = flags
        self.digit = cell.digit

    def __repr__(self):
        return f'NUMBER: {self.digit} with {len(self.closed)} closed and {len(self.flags)} flags'

    @property
    def len_closed(self):
        return len(self.closed)

    @property
    def rest_bombs(self):
        return self.digit - len(self.flags)

def create_roots(matrix):
    """
    Строит "дерево" корней (соседних клеток) для каждой цифры на поле.
    Берутся в учет только те клетки, у которых есть пустые клетки вокруг.
    Для каждой цифры создается объект класса Root, который содержит список закрытых ячеек и список флагов,
    приходящихся на эти ячейки.
    :param matrix:
    :return:
    """
    roots = []
    for cell in matrix.get_digit_cells():
        if len(matrix.around_closed_cells(cell)):
            closed = matrix.around_closed_cells(cell)
            flags = matrix.around_flagged_cells(cell)
            roots.append(Root(cell, closed, flags))
    return roots


def solver_B2(matrix):
    """
    - Для каждой цифры делаем список закрытых ячеек
    - Если один набор полностью входит во второй
    - Из ЦИФРЫ списка (вокруг которой root) вычитаем кол-во уже открытых флагов
    - Сравниваем два корня (каждый с каждым).
    - Находим совпадения:
        `Цифра` первого корня + `Цифра` второго корня + разница в длине между корнями = длина большего корня
        Вот эту разницу - отмечаем бомбами.
    См. иллюстрацию в pic

    r1 = roots[0]
    r2 = roots[1]
    set(r1.closed).issubset(set(r2.closed))  => True если r1 входид в множество r2

    set(r1) ^ set(r2) => set содержащий элементы, которые входят только в одно из множеств (XOR)

    r1.union(r2) => set содержащий все элементы обоих множеств (без дублирования) (OR)
    """
    roots = create_roots(matrix)
    for r1, r2 in itertools.combinations(roots, 2):

        set1 = set(r1.closed)
        set2 = set(r2.closed)
        if set1.issubset(set2) or set2.issubset(set1):
            # сначала я думал убирать возможный знак минус, но именно так получается правильно - даже если будет минус,
            # то в обоих случаях. А если его убрать, возможны коллизии
            diff_len = r1.len_closed - r2.len_closed

            diff_number = r1.rest_bombs - r2.rest_bombs
            if diff_len and (diff_len == diff_number):
                # XOR - возвращает то, что не входит в оба сета.
                # Возвращает тип set. Если нужен список - обернуть в tuple.
                bombs = tuple(set(r1.closed) ^ set(r2.closed))
                # r1.ancestor.mark_cell_debug()
                # r2.ancestor.mark_cell_debug()
                # print('COMPARE', r1.ancestor, r2.ancestor)
                # print(bombs)
                return bombs, 'right'
    return [], Asset.flag


def solver_E2(matrix):
    """
    - Для каждой цифры делаем список закрытых ячеек (Root.closed)
    - При этом нужно из цифры вычесть кол-во флагов (Root.rest_bomb)
    - Сравниваем каждый список с каждым. Ищем вхождение одного списка в другой.
    - Если при этом цифры одинаковые, то все "лишние" ячейки - пустые (их может быть более 1-й)

    На "цифры" влияют флаги - т.е. цифру нужно считать как 'цифра минус флаги вокруг', см. пример solver_e2_2 (п.2)
    :param matrix:
    :return:
    """
    roots = create_roots(matrix)
    answers = []

    for r1, r2 in itertools.combinations(roots, 2):

        set1 = set(r1.closed)
        set2 = set(r2.closed)
        if set1.issubset(set2) or set2.issubset(set1):
            if r1.rest_bombs == r2.rest_bombs:
                empties = tuple(set(r1.closed) ^ set(r2.closed))

                # -- debug
                # r1.ancestor.mark_cell_debug()
                # r2.ancestor.mark_cell_debug()
                # print('-----')
                # print('COMPARE:', r1.ancestor, 'and', r2.ancestor)
                # print('EMPTIES:', empties)
                # return empties, 'left'
                # -- debug

                answers += empties

    return answers, Asset.open
