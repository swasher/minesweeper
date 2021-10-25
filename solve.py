import icecream
from random import randrange
from util import remove_dup
from icecream import ic
import sys
import numpy as np
ic.configureOutput(outputFunction=lambda *a: print(*a, file=sys.stderr))


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

    ### debug
    # ic('------ R1')
    # ic(random_cell)
    # random_cell.mark_cell_debug()
    # input("Press Enter to mouse moving")
    ### end debug

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

        ### debug
        # ic('------ B1')
        # ic(cell)
        # ic(closed, closed, flags)
        # ic(cell.digit, len(closed), len(flags))
        # result = (cell.digit == len(closed) + len(flags)) and len(closed)>0
        # ic(result)
        # cell.mark_cell_debug()
        ### end debug

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

        ### debug
        # ic('------ E1')
        # ic(cell, flags, closed)
        # ic(cell.digit, len(flags), len(closed))
        # result = cell.digit == len(flags) and len(closed)
        # ic(result)
        # cell.mark_cell_debug()
        ### end debug

        if cell.digit == len(flags) and len(closed):
            # cell.mark_cell_debug()
            # не возвращаем ячейки, потому что достаточно кликнуть на саму цифру, чтобы они открылись
            return [cell], 'left'

    # если ни у одной клетки нет решения, возвращаем пустой список
    return [], 'right'
