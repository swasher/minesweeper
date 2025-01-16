from random import randrange
import mouse_controller
from core import Action

def solver_R1_corner(matrix):
    """
    Нажимает рандомную клетку из закрытых.
    Первые 4 - это углы.
    :param matrix:
    :return:
    """

    corner_cells = [matrix.table[0, 0],
                    matrix.table[0, matrix.width-1],
                    matrix.table[matrix.height-1, 0],
                    matrix.table[matrix.height-1, matrix.width-1]
                    ]

    for cell in corner_cells:
        if len(matrix.around_closed_cells(cell)) == 3 and cell.is_closed:
            return [cell], Action.open_cell
    else:
        cells = matrix.get_closed_cells()
        qty = len(cells)
        random_cell = cells[randrange(qty)]
        return [random_cell], Action.open_cell

    # if config.turn_by_turn:
    #     ic('------ R1-corner')
    #     ic(random_cell)
    #     random_cell.mark_cell_debug()
    #     input("Press Enter to mouse moving")


