from random import randrange
import maus

def solver_R1_smart(matrix):
    """
    Нажимает рандомную клетку из закрытых.
    Учитывает, с какой вероятностью в клетке будет бомба
    :param matrix:
    :return:
    """

    common_risk = matrix.bomb_qty / len(matrix.get_closed_cells())
    closed_cells = matrix.get_closed_cells()

    for cell in closed_cells:
        cell.risk = []
        cell.risk.append(common_risk)

    # Каждая "цифра" на игровом поле дает всем окружающим ее закрытым ячейкам некую вероятность,
    # что в них есть бомба - (цифра - флаги) / кол-во закрытых ячеек
    for digit in matrix.get_digit_cells():
        around_closed = matrix.around_closed_cells(digit)
        for cell in around_closed:
            qty_around_flagged = len(matrix.around_flagged_cells(cell))
            qty_around_closed = len(around_closed)
            risk_factor = (digit.digit - qty_around_flagged) / qty_around_closed
            cell.risk.append(risk_factor)

    # Для каждой ячейки оставляем наибольшее значение
    for cell in closed_cells:
        cell.risk = max(cell.risk)

    cell = min(closed_cells, key=lambda r: r.risk)


    cells = matrix.get_closed_cells()
    qty = len(cells)
    random_cell = cells[randrange(qty)]

    # if config.turn_by_turn:
    #     ic('------ R1')
    #     ic(random_cell)
    #     random_cell.mark_cell_debug()
    #     input("Press Enter to mouse moving")

    return [random_cell], maus.OPEN
