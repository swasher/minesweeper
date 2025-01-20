import utils
from core import Action
from core import Cell
from .classes import Turn


def solver_B1(matrix, return_all: bool = False) -> ([Turn], Action):
    """
    B1 - значит ищем Bомбы алгоритомом "один"

    Алгоритм:
    Проверяем все ячейки с цифрами.
    Если цифра в ячейке равно кол-ву соседних закрытых клеток (включая клетки с флагами),
    ТО все оставшиеся неоткрытые клетки - бомбы

    Args:
        matrix: Matrix
        return_all: Если да - возвращаем все найденные решения, если нет - одно, ближайшее к последнему клику.

    Returns:
        solution: list, пустой, содержащий 1 или более объектов Cell
        action: Действие, которое нужно выполнить с найденными ячейками
    """
    action = Action.set_flag
    turns = []

    for cell in matrix.get_digit_cells():
        around_closed = matrix.around_closed_cells(cell)
        around_flags = matrix.around_flagged_cells(cell)

        if (cell.digit == len(around_closed) + len(around_flags)) and len(around_closed) > 0:
            # значит во всех around_closed клетках есть бомбы

            # вариант алгоритма с возвратом первой найденной ячейки
            # можно вернуть одну ячейку
            # return around_closed, 'right'
            if not return_all:
                turn = Turn(cell=around_closed[0], action=action, solver=solver_B1.__name__)
                return [turn]

            for c in around_closed:
                turn = Turn(cell=c, action=action, solver=solver_B1.__name__)
                turns.append(turn)

    if not turns:
        return []

    # В список cells одна и та же ячейка может попасть несколько раз (при анализе разных "цифр"). Убираем дубликаты.
    dedup_turns = utils.remove_dup(turns)
    return dedup_turns


