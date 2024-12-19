import numpy as np

from random import randrange
import maus


def solver_R1(matrix):
    """
    Нажимает рандомную клетку из закрытых.
    :param matrix:
    :return:
    """
    cells = matrix.get_closed_cells()
    qty = len(cells)
    # print(f'click random [from {qty}]')
    random_cell = cells[randrange(qty)]

    # if config.turn_by_turn:
    #     ic('------ R1')
    #     ic(random_cell)
    #     random_cell.mark_cell_debug()
    #     input("Press Enter to mouse moving")

    return [random_cell], maus.OPEN
