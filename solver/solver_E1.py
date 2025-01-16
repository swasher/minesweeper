from core import Cell
from core import Action


def solver_E1(matrix) -> ([Cell], Action):
    """
    E1 значит Empty - ищем потенциально пустые ячейки алгоритмом "один"

    :param matrix:
    :return solution: list, пустой или содержащий 1 объект Cell
    :return Asset.nearby: string, определяющий кнопку мыши

    Алгоритм:
    Проверяем все ячейки с цифрами.
    Если вокруг ячейки с цифрой такое же кол-во флагов, и вокруг есть закрытые
    ячейки, ТО все закрытые ячейки вокруг являются пустыми.

    Алгоритм сканирует все поле по этому принципу, затем выбирает ту ячейку, у которой максимальное кол-во пустых клеток.

    HINT: Такие ячейки можно "вскрыть" левым или "both" кликом - откроются все вокруг.
    КРОМЕ режима noflag - тогда отдаем все нужные ячейки
    """
    cells = []
    action = Action.open_digit

    for cell in matrix.get_digit_cells():
        closed = matrix.around_closed_cells(cell)
        flags = matrix.around_flagged_cells(cell)

        if cell.digit == len(flags) and len(closed):
            cell.nearby_closed = len(matrix.around_closed_cells(cell))
            cells.append(cell)

    if cells:
        solution = [max(cells, key=lambda item: item.nearby_closed)]

        # if config.noflag:
        #     # todo тут говно год... Завязана логика поиска решений на тип игры (noflag)
        #     solution = matrix.around_closed_cells(solution[0])
        #     action = Action.open_cell

        # if config.turn_by_turn:
        #     ic('------ E1')
        #     ic(solution)
        #     solution.mark_cell_debug()
    else:
        # если ни у одной клетки нет решения, возвращаем пустой список
        solution = []

    return solution, action



