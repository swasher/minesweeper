from __future__ import annotations
from typing import TYPE_CHECKING
import random
from random import randrange
import mouse_controller
import config
import icecream as ic
from core import Action

if TYPE_CHECKING:
    from core import Matrix


def solver_R1_smart(matrix: Matrix):
    """
    Нажимает рандомную клетку из закрытых.
    Учитывает, с какой вероятностью в клетке будет бомба
    :param matrix:
    :return:
    """
    action = Action.open_cell

    remain_mines = matrix.get_led_number
    print(f'Led digit: {remain_mines}')

    common_risk = remain_mines / matrix.get_num_closed
    closed_cells = matrix.get_closed_cells()

    for cell in closed_cells:
        cell.risk = []
        cell.risk.append(common_risk)

    # Каждая "цифра" на игровом поле дает всем окружающим ее закрытым ячейкам некую вероятность,
    # что в них есть бомба - (цифра - флаги) / кол-во закрытых ячеек
    for digit in matrix.get_digit_cells():
        around_closed = matrix.around_closed_cells(digit)
        for cell in around_closed:

            # qty_around_flagged = len(matrix.around_flagged_cells(cell))
            # мне кажется, что тут надо поменять cell на digit:
            qty_around_flagged = len(matrix.around_flagged_cells(digit))

            qty_around_closed = len(around_closed)
            risk_factor = (digit.digit - qty_around_flagged) / qty_around_closed
            cell.risk.append(risk_factor)

    # Для каждой ячейки оставляем наибольшее значение
    for cell in closed_cells:
        cell.risk = max(cell.risk)

    debug = True
    if debug:
        for cell in closed_cells:
            cell.debug_text = f"{cell.risk:.2f}".lstrip("0")
        matrix.show_debug_text()

    min_risk = min(closed_cells, key=lambda r: r.risk).risk
    filtered_objects = [cell for cell in closed_cells if cell.risk == min_risk]
    cell = random.choice(filtered_objects)

    # if config.turn_by_turn:
    #     ic('------ R1')
    #     ic(cell)
    #     cell.mark_cell_debug()
    #     input("Press Enter to mouse moving")

    return [cell], action
