import numpy as np
from asset import Asset
from random import randrange


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

    # if config.turn_by_turn:
    #     ic('------ R1')
    #     ic(random_cell)
    #     random_cell.mark_cell_debug()
    #     input("Press Enter to mouse moving")

    return [random_cell], Asset.open
