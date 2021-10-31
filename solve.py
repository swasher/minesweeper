import itertools
from random import randrange
import sys
import numpy as np

from config import config
from icecream import ic



"""
Любой алгоритм должен вернуть список ячеек (или []) и действие с ними (строку 'left' or 'right')

Каждый алгоритм возвращает решения сразу, как только нашел (хотя первоначально была идея возвращать решения
bulk-ом для всей доски, оказалось так не комильфо)
"""


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

    if config.turn_by_turn:
        ic('------ R1')
        ic(random_cell)
        random_cell.mark_cell_debug()
        input("Press Enter to mouse moving")

    return [random_cell], 'left'


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

    for cell in matrix.get_digit_cells():
        closed = matrix.around_closed_cells(cell)
        flags = matrix.around_flagged_cells(cell)

        if config.turn_by_turn:
            ic('------ B1')
            ic(cell)
            ic(closed, closed, flags)
            ic(cell.digit, len(closed), len(flags))
            result = (cell.digit == len(closed) + len(flags)) and len(closed)>0
            ic(result)
            cell.mark_cell_debug()

        if (cell.digit == len(closed) + len(flags)) and len(closed)>0:
            # значит во всех closed клетках есть бомбы
            return closed, 'right'

    # если ни у одной клетки нет решения, возвращаем пустой список
    return [], 'right'


def solver_E1(matrix):
    """
    E1 значит Empty - ищем потенчиально пустые ячейки алгоритмом "один"
    :return: empty list of cells (bombs), list for empty cells, and True if we want click cell themselfe (open all cells around)

    Алгоритм:
    Проверяем все ячейки с цифрами.
    Если вокруг ячейки с цифрой такое же кол-во флагов, и вокруг есть закрытые
    ячейки, ТО все закрытые ячейки вокруг являются пустыми.
    HINT: Такие ячейки можно "вскрыть" левым кликом - откроются все вокруг.
    """
    for cell in matrix.get_digit_cells():
        closed = matrix.around_closed_cells(cell)
        flags = matrix.around_flagged_cells(cell)

        if config.turn_by_turn:
            ic('------ E1')
            ic(cell, flags, closed)
            ic(cell.digit, len(flags), len(closed))
            result = cell.digit == len(flags) and len(closed)
            ic(result)
            cell.mark_cell_debug()

        if cell.digit == len(flags) and len(closed):
            # cell.mark_cell_debug()
            # не возвращаем ячейки, потому что достаточно кликнуть на саму цифру, чтобы они открылись
            return [cell], 'left'

    # если ни у одной клетки нет решения, возвращаем пустой список
    return [], 'right'



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
    return [], 'right'


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
                r1.ancestor.mark_cell_debug()
                r2.ancestor.mark_cell_debug()
                # print('-----')
                # print('COMPARE:', r1.ancestor, 'and', r2.ancestor)
                # print('EMPTIES:', empties)
                # return empties, 'left'
                answers += empties

    return answers, 'left'
