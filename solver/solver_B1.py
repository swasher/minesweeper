import utils
from core import Action
from core import Cell


def solver_B1(matrix, return_all: bool = False) -> ([Cell], Action):
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
    cells = []
    for cell in matrix.get_digit_cells():
        closed = matrix.around_closed_cells(cell)
        flags = matrix.around_flagged_cells(cell)

        if (cell.digit == len(closed) + len(flags)) and len(closed) > 0:
            # значит во всех closed клетках есть бомбы

            # вариант алгоритма с возвратом первой найденной ячейки
            # можно вернуть одну ячейку
            # return closed, 'right'

            for c in closed:
                cells.append(c)

    # В список cells одна и та же ячейка может попасть несколько раз (при анализе разных "цифр"). Убираем дубликаты.
    if cells:
        if return_all:
            cells = utils.remove_dup(cells)
        else:
            cells = utils.remove_dup(cells)[0]

    """
    DEPRECATED
    Алгоритм сортировки сделан в e1b1, а в будующем будет общий для всех алгоритмов
    # Алгоритм B1 выдает серию клеток; сортировать их в порядке "близости" на поле, а то он помечает их в хаотичном порядке
    # Сделано довольно топорно - от сортирует в порядке возрастания расстояния от центра достки.
    # В принцепе работает, но по феншую нужно сделать "ближайшее к текущей позиции", а затем к "новой текущей", типа рекурсии
    center_x = matrix.region_x1 + (matrix.region_x2 - matrix.region_x1)/2
    center_y = matrix.region_y1 + (matrix.region_y2 - matrix.region_y1)/2
    cells = sorted(cells, key=lambda c: math.hypot(center_x - c.coordx, center_y - c.coordy))
    """

    # ic('------ B1')
    # for cell in cells:
        # ic(cell)
        # cell.mark_cell_debug()
    # input('wait...')

    return cells, action
