import utils
from core import Action
from core import Cell
from .classes import Turn


def solver_B1_new(matrix) -> [Turn]:
    """
    B1 - значит ищем (B)ombs алгоритомом "один"

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
    probability = 1
    turns = []

    for cell in matrix.get_digit_cells():
        around_closed = cell.around_closed()
        num_around_closed = len(around_closed)
        num_around_flags = len(cell.around_flagged())

        if (cell.digit == num_around_closed + num_around_flags) and num_around_closed > 0:
            # значит во всех around_closed клетках есть бомбы

            # вариант алгоритма с возвратом первой найденной ячейки
            # можно вернуть одну ячейку
            # return around_closed, 'right'

            for c in around_closed:
                turn = Turn(cell=c, probability=probability, solver=solver_B1_new.__name__)
                turns.append(turn)

    # В список cells одна и та же ячейка может попасть несколько раз (при анализе разных "цифр"). Убираем дубликаты.
    dedup_turns = utils.remove_duplicated_turns(turns)
    return dedup_turns
